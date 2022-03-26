"""
Nomisweb census data interactive query builder
See README.md for details on how to use this package
"""

import ukcensusapi.Nomisweb as ApiEW
import ukcensusapi.NRScotland as ApiSC
import ukcensusapi.NISRA as ApiNI

def _get_scni(table, api, codes):
  meta = { "geographies": {}}
  for k in codes:
    try:
      raw = api.get_metadata(table, k)
      meta["table"] = raw["table"]
      meta["description"] = raw["description"]
      #meta["geographies"] = {}
      meta["geographies"][raw["geography"]] = raw["fields"]
    except ValueError:
      pass
  return meta

def _print_scni(meta):
  for k in meta["geographies"].keys():
    print("Geography: %s" % k)
    for c in meta["geographies"][k]:
      print("  %s:" % c)
      for i, v in meta["geographies"][k][c].items():
        print("    %3d: %s" %(i, v))

class Query:
  """
  Census query functionality
  """
  def __init__(self, cache_dir):
    self.cache_dir = cache_dir
    self.api = ApiEW.Nomisweb(cache_dir)

  def table(self):
    """
    Interactive census table query
    """

    print("Nomisweb census data interactive query builder")
    print("See README.md for details on how to use this package")

    table = input("Census table: ")

    # only init Sc/NI APIs if required (large initial download)
    if table.endswith("SC"):
      api_sc = ApiSC.NRScotland(self.cache_dir)
      print("Data source: NRScotland")
      _print_scni(_get_scni(table, api_sc, ApiSC.NRScotland.GeoCodeLookup.keys()))
      return
    elif table.endswith("NI"):
      api_ni = ApiNI.NISRA(self.cache_dir)
      print("Data source: NISRA")
      _print_scni(_get_scni(table, api_ni, ApiNI.NISRA.GeoCodeLookup.keys()))
      return
    print("Data source: nomisweb (default)")

    query_params = {}
    query_params["date"] = "latest"
    query_params["select"] = "GEOGRAPHY_CODE,"

    # select fields/categories from table
    meta = self.api.get_metadata(table)
    print(meta["description"])
    for field in meta["fields"]:
      if field != "GEOGRAPHY" and field != "FREQ":
        print(field + ":")
        for category in meta["fields"][field]:
          print("  " + str(category) + " (" + meta["fields"][field][category] + ")")
        categories = input("Select categories (default 0): ")
        include = True
        if categories == "" or categories == "0":
          include = input("include in output (y/n, default=n)? ") == "y"
          categories = "0"
        query_params[field] = categories
        if field != "MEASURES" and include:
          query_params["select"] += field + ","

    query_params["select"] += "OBS_VALUE"

    add_geog = input("Add geography? (y/N): ") == "y"
    if add_geog:
      query_params["geography"] = self.__add_geog(meta)
      #print(query_params)

      get_data = input("Get data now? (y/N): ") == "y"
      if get_data:
        print("\n\nGetting data...")

        # Fetch (and cache) data
        self.api.get_data(table, query_params)

    # Remove API key in example code (lest it be accidentally committed)
    if "uid" in query_params:
      del query_params["uid"]

    self.write_code_snippets(table, meta, query_params)

  # returns a geography string that can be inserted into an existing query
  def get_geog_from_names(self, coverage, resolution):
    """
    Return a set of nomisweb geography codes for areas within the specified coverage at the specified resolution
    """

    # Convert the coverage area into nomis codes
    coverage_codes = self.api.get_lad_codes(coverage)
    return self.api.get_geo_codes(coverage_codes, resolution)

  def __add_geog(self, metadata):

    coverage = input("\nGeographical coverage\nE/EW/GB/UK or LAD codes(s)/name(s), comma separated: ")

    if coverage == "E":
      coverage_codes = [ApiEW.Nomisweb.GeoCodeLookup["England"]]
    elif coverage == "EW":
      coverage_codes = [ApiEW.Nomisweb.GeoCodeLookup["EnglandWales"]]
    elif coverage == "GB":
      coverage_codes = [ApiEW.Nomisweb.GeoCodeLookup["GB"]]
    elif coverage == "UK":
      coverage_codes = [ApiEW.Nomisweb.GeoCodeLookup["UK"]]
    else:
      coverage_codes = self.api.get_lad_codes(coverage.split(","))

    #print(metadata)
    for key in metadata["geographies"]:
      print(key, metadata["geographies"][key])

    resolution_valid = False
    while not resolution_valid:
      resolution = input("Select Resolution: ")
      if resolution in metadata["geographies"].keys():
        resolution_valid = True
      else:
        print(resolution + " is not valid")

    area_codes = self.api.get_geo_codes(coverage_codes, resolution)
    return area_codes

  def write_code_snippets(self, table, meta, query_params):
    """
    Write out python and R code snippets, based on the supplied query, for later use
    """
    snippet_file = self.api.cache_dir / (table + ".py")
    print("\nWriting python code snippet to " + str(snippet_file))
    with open(str(snippet_file), "w") as py_file:
      py_file.write("\"\"\"\n" + meta["description"])
      py_file.write("\n\nCode autogenerated by UKCensusAPI\n")
      py_file.write("(https://github.com/virgesmith/UKCensusAPI)\n\"\"\"")
      py_file.write("\n\n# This code requires an API key, see the README.md for details")
      py_file.write("\n\n# Query url:\n# " + self.api.get_url(meta["nomis_table"], query_params))
      py_file.write("\n\nimport ukcensusapi.Nomisweb as CensusApi")
      py_file.write("\n\napi = CensusApi.Nomisweb(\"" + str(self.api.cache_dir) + "\")")
      py_file.write("\ntable = \"" + table + "\"")
      py_file.write("\ntable_internal = \"" + meta["nomis_table"] + "\"")
      py_file.write("\nquery_params = {}")
      for key in query_params:
        py_file.write("\nquery_params[\""+key+"\"] = \""+query_params[key]+"\"")
      if not "geography" in query_params:
        py_file.write("\n# TODO query_params[\"geography\"] = ...")
      py_file.write("\n" + table + " = api.get_data(table, query_params)\n")

    snippet_file = self.api.cache_dir / (table + ".R")
    print("\nWriting R code snippet to " + str(snippet_file))
    with open(str(snippet_file), "w") as r_file:
      r_file.write("# " + meta["description"])
      r_file.write("\n\n# Code autogenerated by UKCensusAPI")
      r_file.write("\n#https://github.com/virgesmith/UKCensusAPI")
      r_file.write("\n\n# This code requires an API key, see the README.md for details")
      r_file.write("\n# Query url: " + self.api.get_url(meta["nomis_table"], query_params))
      r_file.write("\n\nlibrary(\"UKCensusAPI\")")
      r_file.write("\ncacheDir = \"" + str(self.api.cache_dir) + "\"")
      r_file.write("\napi = UKCensusAPI::instance(cacheDir)")
      r_file.write("\ntable = \"" + table + "\"")
      r_file.write("\ntable_internal = \"" + meta["nomis_table"] + "\"")
      r_file.write("\nqueryParams = list(")
      first = True
      for key in query_params:
        if first:
          r_file.write("\n  "+key+" = \""+query_params[key] + "\"")
          first = False
        else:
          r_file.write(",\n  "+key+" = \""+query_params[key] + "\"")
      if not "geography" in query_params:
        r_file.write("\n  # TODO add geography parameter to this query...")
      r_file.write("\n)")
      r_file.write("\n" + table + " = UKCensusAPI::getData(api, table, queryParams)\n")
