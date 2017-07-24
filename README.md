# Overview

This repository contains a Python package that provides an
interface to Twitter's
[Engagement API](http://support.gnip.com/apis/engagement_api/).  
In addition to providing a straightforward interface to the API, this package 
implements extra aggregation features. 
An interface to the [Audience](http://support.gnip.com/apis/audience_api/) API
can be found on the `audience_api` branch.

# Installation

You can pip-install the package:

`$ pip install gnip_insights_interface`

You can also install a local version from the cloned repository location.

`[REPOSITORY] $ pip install -e . -U`

# Credentials

This package expects to find a YAML credentials file called 
`.twitter_api_creds` in your home directory. This files must
contain your [Twitter Oauth credentials](https://dev.twitter.com/oauth/3-legged)
in the following format:

```
username: YOUR_USER_NAME
engagement:
    consumer_key: --
    consumer_secret: --
    token: --
    token_secret: --
    url: https://data-api.twitter.com/insights/engagement
```

# Engagement API Interface

We provide an interface for passing a set of Tweet IDs to the Twitter
Engagement API, which provides engagement data such as impressions, favorites,
and replies.  A full list of the available engagement types, their names, and
the ways that they can be grouped is available in the [API
documentation](http://support.gnip.com/apis/engagement_api/). 

We construct the API interface in a python module called `engagement_api`,
which is part of the `gnip_insights_interface` package.  We provide a script
for command-line interface called `tweet_engagements.py`.  The script provides
direct access the the three endpoint of the API: total counts (`-T`), 28 hour
summary (`-D`, for "day"), as well as an aggregating function (`-H`) which
combines the data from results over an arbitrary time range. See the help option.

Custom groupings and engagements types are set with a YAML configuration file
specified with the `-c` option. See example config in the `example` 
directory in the repository.

