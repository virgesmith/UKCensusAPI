#!/usr/bin/env python3

# TODO move into test harness when appropriate

import ukcensusapi.NRScotland as NRScotland

census = NRScotland.NRScotland("~/.ukpopulation/cache")

categories = census.get_metadata("KS401SC", "LAD")
print(categories)

census.get_data("KS401SC", "LAD")


