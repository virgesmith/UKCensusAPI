#!/usr/bin/python3

from NomiswebApi import NomiswebApi

api = NomiswebApi("../data/", "../persistent_data/laMapping.csv")

print("Nomisweb census data geographical query example")
print("See README.md for details on how to use this package")

# In the previous example we had a predefined query using Leeds at MSOA resolution, 
# but we want to expand the geographical area and refine the resolution
table = "NM_618_1"
queryParams = {}
queryParams["CELL"] = "7...13"
queryParams["date"] = "latest"
queryParams["RURAL_URBAN"] = "0"
queryParams["select"] = "GEOGRAPHY_CODE,CELL,OBS_VALUE"
queryParams["geography"] = "1245710558...1245710660,1245714998...1245714998,1245715007...1245715007,1245715021...1245715022"
queryParams["MEASURES"] = "20100"

# Define the new coverage area in terms of local authorities
coverage = ["Leeds","Bradford"]
# Define the new resolution
resolution = NomiswebApi.OA
# Convert the coverage area into nomis codes
coverageCodes = api.readLADCodes(coverage)
# replace the geography value in the query
queryParams["geography"] = api.geoCodes(coverageCodes, resolution)
# get the data
KS401EWfine = api.getData(table, queryParams)

# Now widen the coverage to England & Wales and coarsen the resolution to LA
queryParams["geography"] = api.geoCodes([NomiswebApi.EnglandWales], NomiswebApi.LAD)
# get the data
KS401EWbroad = api.getData(table, queryParams)


