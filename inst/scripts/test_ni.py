#!/usr/bin/env python3

# TODO move into test harness when appropriate

import ukcensusapi.NISRA as NISRA

census = NISRA.NISRA("~/.ukpopulation/cache")

result = sorted(census.get_geog("95AA", "LSOA11"))
print(result)
result = sorted(census.get_geog("95AA", "OA11"))
print(len(result))


#print(census.get_metadata("LC1101NI", "OA11"))
#d = census.get_data("LC1101NI", "95AA", "LSOA11")
#print(d.head())
#print(len(d))
meta = census.get_metadata("DC1101NI", "LSOA11")

#print(meta)

data = census.get_data("DC1101NI", "95AA", "LSOA11", category_filters={"DC1101NI_0_CODE": 0, "DC1101NI_1_CODE": [1,2], "DC1101NI_2_CODE": [1,2]})
print(data.head())


print(census.get_metadata("QS401NI", "SOA"))
