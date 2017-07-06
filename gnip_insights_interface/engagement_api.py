import requests
import time
import datetime
import json
import logging
import itertools
from dateutil.parser import parse as dt_parser

from .utils import get_query_setup
from .exceptions import *

logger = logging.getLogger('engagements_api')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

def query_tweets(tweet_ids, 
        groupings, 
        endpoint, 
        engagement_types,
        max_tweet_ids = 25,
        date_range = (None,None)
        ):
    """ 
    Return engagements for specified Tweets, groupings
    engagements, and endpoint. 
    Providing start/end times enables historical mode.
    
    There are two iterations to manage:
    - splitting the tweet IDs into acceptably small chunks 
    - splitting the date range into acceptably small chunks
    """ 

    if ( date_range[0] is None and date_range[1] is not None ) or \
    ( date_range[0] is not None and date_range[1] is None ):
        raise DateRangeException("Must specify both or neither of the 'date_range' tuple elements")

    #if datetime.datetime.strptime(date_range[1],'%Y-%m-%d') > datetime.datetime.now():
    #    raise DateRangeException("Tweet was posted less than 27 days ago. Use 'totals' endpoint.")

    MAX_DATE_RANGE_IN_DAYS = 27
    def yield_date_range(start_date, end_date):
        """ yield datetime objects in MAX_DATE_RANGE_IN_DAYS intervals """
        for n in range(0, int((end_date - start_date).days), MAX_DATE_RANGE_IN_DAYS):
            yield start_date + datetime.timedelta(n)

    def chunks(iterable, size=1):  
        """ 
        yield list representations of
        'size'-length, consecutive slices of 'iterable' 
        """
        iterator = iter(iterable)
        for first in iterator:
            yield list(itertools.chain([first], itertools.islice(iterator, size - 1)))
    

    results = {}

    # split tweet ID list into chunks of size 'max_tweet_ids' 
    
    for tweet_ids_chunk in chunks(tweet_ids,max_tweet_ids):  
        results_for_these_ids = {}
        post_data = {
            'tweet_ids' : tweet_ids_chunk,
            'engagement_types' : engagement_types,
            'groupings' : groupings
            } 
        
        if date_range == (None,None):
            # this is '28hr' or 'totals' mode
            results_for_these_ids = make_request(post_data,endpoint)
        else: 
            # this is historical mode
            start_time = dt_parser(date_range[0])
            end_time = dt_parser(date_range[1])
        
            # standard timed query (only one call required)
            if (end_time - start_time).days <= MAX_DATE_RANGE_IN_DAYS:
                start_time = dt_parser(date_range[0])
                end_time = dt_parser(date_range[1])
                post_data['start'] = start_time.strftime('%Y-%m-%d')
                post_data['end'] = end_time.strftime('%Y-%m-%d')
                results_for_these_ids = make_request(post_data,endpoint)
            
            # extended timed query (multiple calls required)
            else:
                # iterate over all chunks of dates
                for this_start_time in yield_date_range(start_time, end_time):
                    this_end_time = this_start_time + datetime.timedelta(MAX_DATE_RANGE_IN_DAYS)
                    if this_end_time > end_time:
                        this_end_time = end_time

                    post_data['start'] = this_start_time.strftime('%Y-%m-%d')
                    post_data['end'] = this_end_time.strftime('%Y-%m-%d')
                    
                    results_for_these_ids_and_dates = make_request(post_data,endpoint)
                    combine_results(results_for_these_ids,results_for_these_ids_and_dates,groupings)
        combine_results(results,results_for_these_ids,groupings)
    return results

def make_request(post_data,endpoint):
    """ Make a POST request """

    # to access engagement data for ALL Tweets, we want blank strings
    # for the 'token' and 'token_secret' credentials. 
    base_url,auth,json_header = get_query_setup(api='engagement')
    # we're rate-limited to 1/s
    time.sleep(1)
    request = requests.post( base_url.rstrip('/') + '/' + endpoint, 
            auth = auth,
            headers = json_header, 
            data = json.dumps( post_data )
            )
    return request.json()
        

def get_posting_datetime(tweet_id):
    """ get posting time for a Tweet """
    url,auth,json_header = get_query_setup()
    request = requests.get('https://api.twitter.com/1.1/statuses/show.json?id=' + str(tweet_id),  
        auth = auth
    )
    posted_time = request.json()['created_at'] 
    return datetime.datetime.strptime(posted_time,"%a %b %d %H:%M:%S +0000 %Y")

def get_n_months_after_post(tweet_id,n):
    """ 
    For the given Tweet ID, return string representation of the
    'n'-th 27-day time interval after posting
    """ 

    if n <= 0:
        logger.error('Must not set n<=0')
        sys.exit(1)
    start_time_dt = get_posting_datetime(tweet_id)
    start_time_dt = start_time_dt + datetime.timedelta(27*n-1)
    start_time = start_time_dt.strftime("%Y-%m-%d")
    end_time = (start_time_dt + datetime.timedelta(27)).strftime("%Y-%m-%d")
    return start_time,end_time 

def combine_results(results,this_result,groupings):
    """ Combine engagements data from different date ranges or Tweets """
    
    # start by combining results defined in the groupings
    for grouping_name,grouping in groupings.items():
        
        if grouping_name not in results:
            results[grouping_name] = {}
        if grouping_name not in this_result:
            continue
        
        if len(grouping['group_by']) == 2:
            # this is a tweet-ID:engagement:count type of result
            
            for level_1_key in this_result[grouping_name]:
                if level_1_key not in results[grouping_name]:
                    results[grouping_name][level_1_key] = {}
                
                for engagement,count in this_result[grouping_name][level_1_key].items():
                    if engagement in results[grouping_name][level_1_key]:
                        results[grouping_name][level_1_key][engagement] += int(count)
                    else:
                        results[grouping_name][level_1_key][engagement] = int(count)
        
        if len(grouping['group_by']) == 3:
            # this is a tweet-ID:time-bucket:engagement:count type of result
           
            for level_1_key in this_result[grouping_name]:
                if level_1_key not in results[grouping_name]:
                    results[grouping_name][level_1_key] = {}
                
                for engagement,date_data in this_result[grouping_name][level_1_key].items(): 
                    if engagement not in results[grouping_name][level_1_key]:
                        results[grouping_name][level_1_key][engagement] = {}
                    for date,count in this_result[grouping_name][level_1_key][engagement].items():
                        if date in results[grouping_name][level_1_key][engagement]:
                            results[grouping_name][level_1_key][engagement][date] += int(count)
                        else:
                            results[grouping_name][level_1_key][engagement][date] = int(count)
    
    # do keys not in groupings, such as errors
    for other_key in this_result.keys():
        if other_key in groupings:
            continue
        if other_key in ['start','end']:
            results[other_key] = this_result[other_key]
            continue
        if other_key not in results:
            results[other_key] = []
        results[other_key].extend(this_result[other_key])





