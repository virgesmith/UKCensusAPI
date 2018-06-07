#!/usr/bin/env python3

# TODO move into test harness when appropriate

import ukcensusapi.NRScotland as NRScotland

census = NRScotland.NRScotland("~/.ukpopulation/cache")

meta = census.get_metadata("KS401SC", "LAD")
print(meta)

meta = census.get_metadata("DC1117SC", "LAD")
print(meta)
meta = census.get_metadata("DC2101SC", "LAD")
print(meta)

table = census.get_data("KS401SC", "LAD", "S12000033", category_filters={"KS401SC_0_CODE": range(8,15)})
print(table)

table = census.get_data("DC1117SC", "LAD", "S12000033")
print(table)

table = census.get_data("DC2101SC", "LAD", "S12000033", category_filters={
  "DC2101SC_0_CODE": 4, # white irish
  "DC2101SC_1_CODE": [1,2], # male & female
  "DC2101SC_2_CODE": range(6,13) # 18-49
  })
print(table.shape)

table = census.contextify(table, meta, "DC2101SC_2_CODE")
print(table)

