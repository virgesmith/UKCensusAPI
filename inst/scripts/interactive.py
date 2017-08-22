#!/usr/bin/env python3

# Disable "Invalid constant name"
# pylint: disable=C0103

# -*- coding: utf-8 -*-
"""
interactive census table query
"""

import ukcensusapi.Nomisweb as CensusApi
import ukcensusapi.Query as Census

# intialise the API using current directory as the cache directory
api = CensusApi.Nomisweb("/tmp/UKCensusAPI")

# initialise the census query
census = Census.Query(api)

# run the interactive query
census.table()
