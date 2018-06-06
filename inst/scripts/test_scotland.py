#!/usr/bin/env python3

# TODO move into test harness when appropriate

import ukcensusapi.NRScotland as NRScotland

census = NRScotland.NRScotland("~/.ukpopulation/cache")

meta = census.get_metadata("KS401SC", "LAD")
#print(meta)

table = census.get_data("KS401SC", "LAD", "S12000033")
print(table)

table = census.contextify(table, meta)
print(table)



