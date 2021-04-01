import os
import yaml
from requests_oauthlib import OAuth1

from .exceptions import CredentialsException

def get_query_setup(api="engagement"):
    """ 
    Do authentication and credentials stuff
    
    The 'api' keyword-argument must be 'engagment'. 

    """

    if api == 'audience':
        raise CredentialsException("Audience API interface is no longer supported")
    if api != 'engagement':
        raise CredentialsException("'api' keyword-argument to get_query_setup must be 'engagment'")

    creds_file_path = os.getenv('HOME') + '/.twitter_api_creds'
    if os.path.exists(creds_file_path):
        with open(creds_file_path, 'r') as f:
            creds = yaml.load(f)
            url = creds[api]['url']
    elif "TWITTER_CONSUMER_KEY" in os.environ:
        creds = {}
        creds[api] = {}
        creds[api]['consumer_key'] = os.environ["TWITTER_CONSUMER_KEY"]
        creds[api]['consumer_secret'] = os.environ["TWITTER_CONSUMER_SECRET"]
        creds[api]['token'] = os.environ["TWITTER_ACCESS_TOKEN"]
        creds[api]['token_secret'] = os.environ["TWITTER_ACCESS_TOKEN_SECRET"]
        url = os.environ["TWITTER_ENGAGEMENT_URL"]
    else:
        raise CredentialsException('Credentials file at $HOME/.twitter_api_creds must exists!') 
    
    try:
        auth = OAuth1(creds[api]['consumer_key'],creds[api]['consumer_secret'],creds[api]['token'],creds[api]['token_secret'])
    except (TypeError,KeyError) as e:
        raise CredentialsException(
            '''Credentials file at $HOME/.twitter_api_creds contain the keys: username, consumer_key, 
            consumer_secret, token, token_secret, url
            or Environment variables TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, 
            TWITTER_ACCESS_TOKEN_SECRET, must exist''')
    json_header = {'Content-Type' : 'application/json'}

    return url,auth,json_header
