import os
import yaml
from requests_oauthlib import OAuth1

from .exceptions import CredentialsException

def get_query_setup(no_token_creds=False):
    """ 
    Set up credentials and authentication 
    """
    creds_file_path = os.getenv('HOME') + '/.twitter_api_creds'
    if not os.path.exists(creds_file_path): 
        raise CredentialsException('Credentials file at $HOME/.twitter_api_creds must exists!') 
    creds = None
    with open(creds_file_path,'r') as f:
        creds = yaml.load(f)

        if no_token_creds:
            try:
                auth = OAuth1(creds['consumer_key'],creds['consumer_secret'],"","")
            except (TypeError,KeyError) as e:
                raise CredentialsException('Credentials file at $HOME/.twitter_api_creds must contain the keys: username, consumer_key, consumer_secret, url') 
        else:
            try:
                auth = OAuth1(creds['consumer_key'],creds['consumer_secret'],creds['token'],creds['token_secret'])  
            except (TypeError,KeyError) as e:
                raise CredentialsException('Credentials file at $HOME/.twitter_api_creds must contain the keys: username, consumer_key, consumer_secret, token, token_secret, url') 
    json_header = {'Content-Type' : 'application/json'}

    return creds,auth,json_header
