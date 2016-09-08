#!/usr/bin/env python

import sys
import os
import datetime
import argparse
import json

from gnip_insights_interface import audience_api

parser = argparse.ArgumentParser()
parser.add_argument('-i','--input-file-name',dest='input_file_name',default=None,
        help='unique identifier to be applied to output file names; default is %(default)s')
args = parser.parse_args()

# set up inputs
if args.input_file_name is not None:
    user_ids = open(args.input_file_name)
else:
    user_ids = sys.stdin

# set default groupings
groupings_dict = {"groupings": {
    "gender": {"group_by": ["user.gender"]}
    , "location_country": {"group_by": ["user.location.country"]}
    , "location_country_region": {"group_by": ["user.location.country", "user.location.region"]}
    , "interest": {"group_by": ["user.interest"]}
    , "tv_genre": {"group_by": ["user.tv.genre"]}
    , "device_os": {"group_by": ["user.device.os"]}
    , "device_network": {"group_by": ["user.device.network"]}
    , "language": {"group_by": ["user.language"]}
}}
groupings = json.dumps(groupings_dict)

# analyze and output
results_json = audience_api.query_users(user_ids, groupings) 
results = json.dumps(results_json)
sys.stdout.write(results + '\n')
