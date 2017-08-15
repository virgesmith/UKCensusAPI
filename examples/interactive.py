#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""
interactive census table query
"""

import ukcensusapi.Nomisweb as CensusApi
import ukcensusapi.Query as Census

# intialise the API using current directory as the cache directory
API = CensusApi.Nomisweb("./")

# initialise the census query
CENSUS = Census.Query(API)

# run the interactive query
CENSUS.table()
