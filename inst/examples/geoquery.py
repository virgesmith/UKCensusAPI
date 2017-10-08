#!/usr/bin/env python3

import ukcensusapi.Nomisweb as Api

def main():
  api = Api.Nomisweb("/tmp/UKCensusAPI")

  print("Nomisweb census data geographical query example")
  print("See README.md for details on how to use this package")

  # In the previous example we had a predefined query using Leeds at MSOA resolution,
  # but we want to expand the geographical area and refine the resolution
  table = "KS401EW"
  table_internal = "NM_618_1"
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
  resolution = Api.Nomisweb.OA11
  # Convert the coverage area into nomis codes
  coverage_codes = api.get_lad_codes(coverage)
  # replace the geography value in the query
  query_params["geography"] = api.get_geo_codes(coverage_codes, resolution)
  # get the data
  ks401fine = api.get_data(table, table_internal, query_params)
  print(ks401fine.head(5))

  # Now widen the coverage to England & Wales and coarsen the resolution to LA
  coverage_codes = [Api.Nomisweb.EnglandWales]
  resolution = Api.Nomisweb.LAD
  query_params["geography"] = api.get_geo_codes(coverage_codes, resolution)
  # get the data
  ks401broad = api.get_data(table, table_internal, query_params)
  print(ks401broad.head(5))

if __name__ == "__main__":
  main()
