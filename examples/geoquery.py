#!/usr/bin/env python3

# Disable "Invalid constant name"
# pylint: disable=C0103

import pandas as pd
import ukcensusapi.Nomisweb as Api

API = Api.Nomisweb("./")

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
coverage_codes = API.get_lad_codes(coverage)
# replace the geography value in the query
query_params["geography"] = API.get_geo_codes(coverage_codes, resolution)
# get the data
KS401FINE = API.get_data(TABLE, query_params)
print(KS401FINE.head(5))

# Now widen the coverage to England & Wales and coarsen the resolution to LA
coverage_codes = [Api.Nomisweb.EnglandWales]
resolution = Api.Nomisweb.LAD
query_params["geography"] = API.get_geo_codes(coverage_codes, resolution)
# get the data
KS401BROAD = API.get_data(TABLE, query_params)
print(KS401BROAD.head(5))


