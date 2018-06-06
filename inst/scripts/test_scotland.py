#!/usr/bin/env python3

# TODO move into test harness when appropriate

import ukcensusapi.NRScotland as NRScotland

census = NRScotland.NRScotland("~/.ukpopulation/cache")

meta, _ = census.get_metadata("KS401SC", "LAD")
print(meta)


meta, _ = census.get_metadata("DC1117SC", "LAD")
print(meta)
meta, _ = census.get_metadata("DC2101SC", "LAD")
print(meta)

table = census.get_data("KS401SC", "LAD", "S12000033")
print(table)
table = census.get_data("DC1117SC", "LAD", "S12000033")
print(table)
table = census.get_data("DC2101SC", "LAD", "S12000033")
print(table.shape)

table = census.contextify(table, meta, "DC2101SC_2_CODE")
print(table)

