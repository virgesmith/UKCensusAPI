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
  query_params["geography"] = "1245710558...1245710660"
  query_params["MEASURES"] = "20100"

  ks401 = api.get_data(table, table_internal, query_params)
  print(ks401.head(5))

  # load the metadata (assumes it is cached, use get_metadata otherwise)
  metadata = api.load_metadata(table)

  # Now add context - the desriptions ofr the values 7 to 13 in the CELL column
  api.contextify(ks401, "CELL", metadata)
  print(ks401.head(5))

if __name__ == "__main__":
  main()
