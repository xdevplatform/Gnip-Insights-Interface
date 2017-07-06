#!/usr/bin/env python

import argparse
import json
import sys
import datetime
import yaml

import gnip_insights_interface.engagement_api as api

parser = argparse.ArgumentParser()
parser.add_argument('-i',dest='tweet_ids',default=[],nargs='+',
        metavar='TWEET_ID',
        help="tweet IDs to analyze")
parser.add_argument('-f',dest='tweet_ids_file',default=None, 
        help="file name containing Tweet IDs to analyze")
parser.add_argument('-T','--total',dest='do_total',default=False,
        action='store_true',
        help="return engagement totals")
parser.add_argument('-D','--28hr',dest='do_28hr',default=False,
        action='store_true',
        help="return engagement data for the previous 28 hours")
parser.add_argument('-H','--historical',dest='do_historical',default=(None,None),nargs=2,
        metavar=('START_TIME','STOP_TIME'),
        help="return engagement data for START_TIME - STOP_TIME; format is YYYY-MM-DD")
parser.add_argument('-M','--month',dest='do_month',default=False,
        action='store_true',
        help="return engagement data for 27 days after post time")
parser.add_argument('-c','--config-file',dest='config_file',default=None,
        help="YAML config file to specify groupings and engagement types")
args = parser.parse_args()

if args.tweet_ids != [] and args.tweet_ids_file is not None:
    sys.stderr.write('Ambiguous input! Must not specify both "-i" and "-f" options!. Exiting.\n') 
    sys.exit(1)
if [args.do_total,args.do_28hr,(args.do_historical != (None,None)),args.do_month].count(True) != 1:
    sys.stderr.write('Must specify exactly one of the options: [-T,-D,-H,-M]. Exiting.\n')
    sys.exit(1)

if args.tweet_ids_file is None and args.tweet_ids == []:
    input_generator = sys.stdin
    sys.stderr.write('Reading Tweet IDs from stdin.\n') 
elif args.tweet_ids_file is not None:
    input_generator = open(args.tweet_ids_file)
else:
    input_generator = args.tweet_ids

# default groupings and engagement_types
groupings = {'totals': {'group_by' : ['tweet.id','engagement.type']},
        }
engagement_types = ['impressions'] 

if args.config_file is not None:
    config = yaml.load(open(args.config_file))
    if 'engagement' in config:
        if 'groupings' in config['engagement']:
            groupings = config['engagement']['groupings']
        if 'engagement_types' in config['engagement']:
            engagement_types = config['engagement']['engagement_types']

if args.do_total:
    endpoint = 'totals' 
    max_tweet_ids = 250
if args.do_28hr:
    endpoint = '28hr'
    max_tweet_ids = 25
if args.do_historical != (None,None):
    endpoint = 'historical'
    max_tweet_ids = 25
start_time = args.do_historical[0]
end_time = args.do_historical[1]

if args.do_month:
    input_generator = list(input_generator)
    if len( input_generator ) > 1:
        sys.stderr.write('Month option (-M) not implemented for more than one Tweet ID\n') 
        sys.exit(1)
    endpoint = 'historical'
    max_tweet_ids = 1
    start_time,end_time = api.get_n_months_after_post(input_generator[0],1)
    if datetime.datetime.strptime(end_time,'%Y-%m-%d') > datetime.datetime.now():
        sys.stderr.write("Tweet was posted less than 27 days ago. Use 'totals' endpoint (-T)\n")
        sys.exit(1)

results = api.query_tweets(input_generator,
        groupings,
        endpoint,
        engagement_types,
        max_tweet_ids,
        (start_time,end_time),
        )
sys.stdout.write( json.dumps(results) + '\n')

