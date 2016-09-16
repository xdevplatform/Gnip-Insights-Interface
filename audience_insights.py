#!/usr/bin/env python

import sys
import os
import datetime
import argparse
import json
import yaml

from gnip_insights_interface import audience_api

parser = argparse.ArgumentParser()
parser.add_argument('-i','--input-file-name',dest='input_file_name',default=None,
        help='unique identifier to be applied to output file names; default is %(default)s'),
parser.add_argument('-c','--config-file',dest='config_file',default=None,
        help="YAML config file to specify groupings")
args = parser.parse_args()

# set up inputs
if args.input_file_name is not None:
    user_ids = open(args.input_file_name)
else:
    user_ids = sys.stdin

# set default groupings
groupings_dict = {"groupings": {
    "gender": {"group_by": ["user.gender"]},
    "language": {"group_by": ["user.language"]},
}}
if args.config_file is not None:
    groupings_dict = {"groupings": yaml.load(open(args.config_file))['audience']['groupings']}
groupings = json.dumps(groupings_dict)

# analyze and output
results_json = audience_api.query_users(user_ids, groupings) 
results = json.dumps(results_json)
sys.stdout.write(results + '\n')
