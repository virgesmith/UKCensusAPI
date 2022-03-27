#!/usr/bin/env python3

from typing import Optional
import pandas as pd

"""
Example of adding context to a table
"""

from ukcensusapi.nomisweb import api_ew


def main(cache_dir: Optional[str]) -> None:
  api = api_ew(cache_dir=cache_dir)

  print("Nomisweb census data geographical query example")
  print("See README.md for details on how to use this package")

  # Heres predefined query on a small geographical area
  table = "KS401EW"
  query_params = {}
  query_params["CELL"] = "7...13"
  query_params["date"] = "latest"
  query_params["RURAL_URBAN"] = "0"
  query_params["select"] = "GEOGRAPHY_CODE,CELL,OBS_VALUE"
  query_params["geography"] = "1245710558...1245710560"
  query_params["MEASURES"] = "20100"

  ks401 = api.get_data(table, query_params)
  # display the first ten rows
  print(ks401.head(10))

  # Now add context - the desriptions of the values (7 to 13) in the CELL column
  api.contextify(table, "CELL", ks401)
  print(ks401.head(10))
  ks401.to_csv("/tmp/contextified", sep="\t")

if __name__ == "__main__":
  main() # uses default cache_dir
