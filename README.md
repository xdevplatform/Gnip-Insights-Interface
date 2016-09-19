# Overview

This repository contains a Python package and executable scripts that provide
interfaces to the Gnip/Twitter
[Audience](http://support.gnip.com/apis/audience_api/) and
[Engagement](http://support.gnip.com/apis/engagement_api/) APIs. In addition
to providing a straightforward interface to the Engegement API, this package 
provides extra aggregation features. For the Audience API,
this package provides a simplified interface for querying a single input set of
user IDs.

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

`
username: YOUR_USER_NAME
audience:
    consumer_key: --
    consumer_secret: --
    token: --
    token_secret: --
    url: https://data-api.twitter.com/insights/audience
engagement:
    consumer_key: --
    consumer_secret: --
    token: --
    token_secret: --
    url: https://data-api.twitter.com/insights/engagement
`
Depending on your Gnip account setup, you may have different credentials
for the audience and engagement APIs.

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

# Audience API Interface

We provide an interface for passing a set of Twitter user IDs to the Twitter
Audience API, which provides aggregate demographic data about those users such
as language, interest, gender, and location.  A full list of the available
demographic types, their names, and the ways that they can be grouped is
available in the [API
documentation](http://support.gnip.com/apis/audience_api/). 

As with the Engagement interface, we construct the API interface in a python
module called `audience_api`, which is part of the `gnip_insights_interface`
package.  We provide a script for command-line interface called
`audience_insights.py`. Custom groupings can be set with a YAML configuration
file specified with the `-c` option. See example in the `example` directory 
of the repository.

Critically, this interface makes a key simplification: that a set of unique
Twitter user IDs will always be associated with the same segment(s) and
audience. This simplification can significantly reduce the number of redundant
segments and audiences. However, this tool can **not** be used for any operation
in which the user wishes to create an audience from segments loaded from
different lists of Twitter user IDs.

The Audience API interface implements this simplification by sorting and
hashing the input user ID set, thus creating a unique identifier for each 
input set of IDs. This identifier is then used as the base name for the one or more
segments that contain the user IDs, and as the name for the
audience associated with that segment or segments. Multiple segments will only
be created when the size of the input set of user IDs exceeds the maximum
segment size. If segments and audiences with names matching the input identifier
are not found, they will be created, then the audience queried. If they are found,
the existing audience will simply be queried.





