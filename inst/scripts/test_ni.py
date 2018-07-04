#!/usr/bin/env python3

# TODO move into test harness when appropriate

import ukcensusapi.NISRA as NISRA

census = NISRA.NISRA("~/.ukpopulation/cache")

# print(NISRA._ni_resolution("LAD"))
# print(NISRA._ni_resolution("LGD"))
# print(NISRA._ni_resolution("WARD"))
# print(NISRA._ni_resolution("MSOA11"))
# print(NISRA._ni_resolution("SOA"))
# print(NISRA._ni_resolution("LSOA11"))
# print(NISRA._ni_resolution("SA"))
# print(NISRA._ni_resolution("OA11"))

result = sorted(census.get_geog("N92000002", "LAD"))
print(result)
result = sorted(census.get_geog("95AA", "LAD"))
print(result)
result = sorted(census.get_geog("95AA", "MSOA11"))
print(result)
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

# {
#   'table': 'QS401NI', 
#   'description': '', 
#   'geography': 'SOA', 
#   'fields': {
#     'QS401NI_0_CODE': {
#       0: 'All usual residents in households', 
#       1: 'Shared dwelling', 
#       2: 'Unshared dwelling: Caravan or othermobile or temporary structure', 
#       3: 'Unshared dwelling: Flat, maisonette or apartment: In a commercial building', 
#       4: 'Unshared dwelling: Flat, maisonette or apartment: Part of a converted or shared house (including bed-sits)', 
#       5: 'Unshared dwelling: Flat, maisonette or apartment: Purpose-built block of flats or tenement', 
#       6: 'Unshared dwelling: Flat, maisonette or apartment: Total', 
#       7: 'Unshared dwelling: Total', 
#       8: 'Unshared dwelling: Whole house or bungalow: Detached', 
#       9: 'Unshared dwelling: Whole house or bungalow: Semi-detached', 
#       10: 'Unshared dwelling: Whole house or bungalow: Terraced (including end-terrace)', 
#       11: 'Unshared dwelling: Whole house or bungalow: Total'
#     }
#   }
# }

print(census.get_data("QS401NI", "95AA", "LAD"))

print(census.get_metadata("QS202NI", "MSOA11"))