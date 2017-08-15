#!/usr/bin/python3

import ukcensusapi.Nomisweb as Api

api = Api.Nomisweb("./")

print("Nomisweb census data geographical query example")
print("See README.md for details on how to use this package")

# In the previous example we had a predefined query using Leeds at MSOA resolution,
# but we want to expand the geographical area and refine the resolution
TABLE = "NM_618_1"
query_params = {}
query_params["CELL"] = "7...13"
query_params["date"] = "latest"
query_params["RURAL_URBAN"] = "0"
query_params["select"] = "GEOGRAPHY_CODE,CELL,OBS_VALUE"
query_params["geography"] = "1245710558...1245710660,1245714998...1245714998,1245715007...1245715007,1245715021...1245715022"
query_params["MEASURES"] = "20100"

# Define the new coverage area in terms of local authorities
coverage = ["Leeds", "Bradford"]
# Define the new resolution
resolution = Api.Nomisweb.OA
# Convert the coverage area into nomis codes
coverage_codes = api.getLADCodes(coverage)
# replace the geography value in the query
query_params["geography"] = api.geoCodes(coverage_codes, resolution)
# get the data
KS401FINE = api.getData(TABLE, query_params)
head(KS401FINE, 5)

# Now widen the coverage to England & Wales and coarsen the resolution to LA
query_params["geography"] = api.geoCodes([Api.Nomisweb.EnglandWales], Api.Nomisweb.LAD)
# get the data
KS401BROAD = api.getData(TABLE, query_params)


