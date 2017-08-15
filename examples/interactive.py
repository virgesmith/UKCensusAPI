#!/usr/bin/env python3

# interactive table query

import ukcensusapi.Nomisweb as Api
import ukcensusapi.Query as Census

# intialise the API using current directory as the cache directory
api = Api.Nomisweb("./")

# initialise the census query
census = Census.Query(api)

# run the interactive query
census.table()

