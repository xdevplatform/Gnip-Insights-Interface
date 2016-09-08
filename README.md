# Overview

This repository contains a Python package and executable scripts that provide
interfaces to the Gnip/Twitter
[Audience](http://support.gnip.com/apis/audience_api/) and
[Engagement](http://support.gnip.com/apis/engagement_api/) APIs.

# Installation

You can install a local version from the cloned repository location.

`[REPOSITORY] $ pip install gnip_insights_interface -U`

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
summary (`-D`, for "day"),  as well as an aggregating function (`-H`) which
combines the data from results over an arbitrary time range. See the help menu.

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
`audience_insights.py`.

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





