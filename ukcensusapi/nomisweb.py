"""
Nomisweb API.
"""
import os
import json
import hashlib
import warnings
from typing import Any, Optional, Union
from pathlib import Path
from collections import OrderedDict
from urllib import request
from urllib.error import HTTPError
from urllib.error import URLError
from urllib.parse import urlencode
from socket import timeout
import pandas as pd  # type: ignore
from functools import lru_cache
from dotenv import load_dotenv
load_dotenv()

import ukcensusapi.utils as utils
from ukcensusapi import CensusAPI


def _get_api_key(cache_dir: Path) -> Optional[str]:
  """
  Look for key in file NOMIS_API_KEY in cache dir, falling back to env var
  """
  filename = cache_dir / "NOMIS_API_KEY"
  if filename.exists():
    with open(filename, "r") as file:
      content = file.read().splitlines()
      # return 1st line (if present)
      if len(content):
         return content[0]
  return os.getenv("NOMIS_API_KEY")


def _shorten(code_list: list[int]) -> str:
  """
  Shortens a list of numeric nomis geo codes into a string format where contiguous values are represented as ranges, e.g.
  1,2,3,6,7,8,9,10 -> "1...3,6,7...10"
  which can drastically reduce the length of the query url
  """
  # empty evals to False
  if not code_list:
    return ""
  if len(code_list) == 1:
    return str(code_list[0])

  code_list.sort() # assume this is a modifying operation
  short_string = ""
  index0 = 0
  index1 = 0 # appease lint
  for index1 in range(1, len(code_list)):
    if code_list[index1] != (code_list[index1 - 1] + 1):
      if index0 == index1:
        short_string += str(code_list[index0]) + ","
      else:
        short_string += str(code_list[index0]) + "..." + str(code_list[index1 - 1]) + ","
      index0 = index1
  if index0 == index1:
    short_string += str(code_list[index0])
  else:
    short_string += str(code_list[index0]) + "..." + str(code_list[index1])
  return short_string


# The core functionality for accessing the www.nomisweb.co.uk API
class Nomisweb(CensusAPI):
  """
  Nomisweb API methods and data.
  """

  # static constants
  URL = "https://www.nomisweb.co.uk/"

  # timeout for http requests
  TIMEOUT = 15

  # # Define Nomisweb geographic area codes, see e.g.
  # https://www.nomisweb.co.uk/api/v01/dataset/NM_144_1/geography/2092957703TYPE464.def.sdmx.json
  # https://www.nomisweb.co.uk/api/v01/dataset/NM_1_1/geography/2092957703TYPE464.def.sdmx.json
  GEOCODE_LOOKUP = {
    # give meaning to some common nomis geography types/codes
    "LAD": "TYPE464",
    "MSOA11": "TYPE297",
    "LSOA11": "TYPE298",
    "OA11": "TYPE299",
    "MSOA01": "TYPE305",
    "LSOA01": "TYPE304",
    "OA01": "TYPE310",
    "England": "2092957699",
    "EnglandWales": "2092957703",
    "GB": "2092957698",
    "UK": "2092957697"
  }

  cache_dir: Path

  cached_lad_codes: Any


  # initialise, supplying a location to cache downloads
  def __init__(self, *, cache_dir: Optional[str], verbose: bool=False) -> None:
    """Constructor.
    Args:
        cache_dir: cache directory
    Returns:
        an instance.
    """
    self.cache_dir = utils.init_cache_dir(cache_dir)
    self.verbose = verbose
    self.offline_mode = True

    # how best to deal with site unavailable...
    self.offline_mode = not utils.check_online(self.URL, Nomisweb.TIMEOUT)
    if self.offline_mode:
      print(f"Unable to contact {self.URL}, operating in offline mode - pre-cached data only")

    self.key = _get_api_key(self.cache_dir)
    if not self.offline_mode and self.key is None:
      raise RuntimeError("""No API key found. Whilst downloads still work, they may be truncated
                            causing potentially unforseen problems in any modelling/analysis.
                            Set the key value in the environment variable NOMIS_API_KEY" \
                            Register at www.nomisweb.co.uk to obtain a key.
                         """)

    if self.verbose: print("Cache directory: ", self.cache_dir)

    # static member
    Nomisweb.cached_lad_codes = self.__cache_lad_codes()

  def get_geo_codes(self, la_codes: Union[str, int, list[str], list[int]], code_type: str) -> str:
    """Get nomis geographical codes.

    Args:
        la_codes: local authority codes for the region
        code_type: enumeration specifying the geographical resolution
    Returns:
        a string representation of the codes.
    """
    # force input to be a list
    if not isinstance(la_codes, list):
      la_codes = [la_codes]

    geo_codes = []
    for i in range(0, len(la_codes)):
      path = "api/v01/dataset/NM_144_1/geography/" + str(la_codes[i]) + code_type + ".def.sdmx.json?"
      rawdata = self.__fetch_json(path, {})

      # use try-catch block to deal with any issues arising from the returned json
      # which are likely due to invalid/empty LA codes
      try:
        n_results = len(rawdata["structure"]["codelists"]["codelist"][0]["code"])
        # seems a bit daft not to take advantage of the fact we know the length
        for j in range(0, n_results):
          geo_codes.append(rawdata["structure"]["codelists"]["codelist"][0]["code"][j]["value"])
      except (KeyError, ValueError):
        print(la_codes[i], " does not appear to be a valid LA code")
    return _shorten(geo_codes)

  def get_lad_codes(self, la_names: Union[str, list[str]]) -> list[str]:
    """Convert local autority name(s) to nomisweb codes.
    Args:
        la_names: one or more local authorities (specify either the name or the ONS code)
    Returns:
        codes.
    """
    if not isinstance(la_names, list):
      la_names = [la_names]
    codes = []
    for la_name in la_names:
      if la_name in Nomisweb.cached_lad_codes:
        codes.append(Nomisweb.cached_lad_codes[la_name])
    return codes

  def get_url(self, table_internal: str, query_params: dict[str, Any]) -> str:
    """Constructs a query url given a nomisweb table code and a query.
    Args:
        table_internal: nomis table code. This can be found in the table metadata
        query_params: a dictionary of parameters and values
    Returns:
        the url that can be used to download the data
    """

    # python dicts have nondeterministic order, see
    # https://stackoverflow.com/questions/14956313/why-is-dictionary-ordering-non-deterministic
    # this is problematic for the cacheing (md5 sum dependent on order), so we insert alphabetically
    # into an OrderedDict (which preserves insertion order)
    ordered = OrderedDict()
    for key in sorted(query_params):
      ordered[key] = query_params[key]

    return f"{Nomisweb.URL}api/v01/dataset/{table_internal}.data.tsv?{str(urlencode(ordered))}"

  # r_compat forces function to return strings (either cached filename, or error msg)
  # Two reasons for this:
  # - pandas/R dataframes conversion is done via matrix (which drops col names)
  # - reporting errors to R is useful (print statements aren't displayed in R(Studio))
  def get_data(self, table: str, query_params: dict[str, Any], r_compat: bool=False) -> pd.DataFrame:
    """Downloads or retrieves data given a table and query parameters.
    Args:
       table: ONS table name, or nomisweb table code if no explicit ONS name
       query_params: table query parameters
       r_compat: return values suitable for R
    Returns:
        a dataframe containing the data. If downloaded, the data is also cached to a file
    """

    # load the metadata
    metadata = self.load_metadata(table)

    query_params["uid"] = self.key
    query_string = self.get_url(metadata["nomis_table"], query_params)
    filename = self.cache_dir / (table + "_" + hashlib.md5(query_string.encode()).hexdigest()+".tsv")

    # retrieve if not in cache
    if not os.path.isfile(str(filename)):
      if self.verbose: print("Downloading and cacheing data: " + str(filename))
      #'TODO migrate to requests package
      request.urlretrieve(query_string, str(filename)) #, timeout = Nomisweb.Timeout)

      # check for empty file, if so delete it and report error
      if os.stat(str(filename)).st_size == 0:
        os.remove(str(filename))
        print("ERROR: Query returned no data. Check table and query parameters")
        return pd.DataFrame()
    else:
      if self.verbose:
        print("Using cached data: " + str(filename))

    # now load from cache and return
    if r_compat:
      return str(filename) # R expects a string not a Path
    data = pd.read_csv(str(filename), delimiter='\t')
    if len(data) == 1000000:
      warnings.warn("Data download has reached nomisweb's single-query row limit. Truncation is extremely likely")
    return data

  def get_metadata(self, table_name: str, resolution: Optional[str] = None) -> dict[str, Any]:
    """Downloads census table metadata.
    Args:
      table_name: the (ONS) table name, e.g. KS4402EW
    Returns:
      a dictionary containing information about the table contents including categories and category values.
    """
    if resolution:
      print("Warning: ignoring the (geographical) resolution parameter when extracting table metadata")

    # see if already downloaded
    if not table_name.startswith("NM_"):
      path = "api/v01/dataset/def.sdmx.json?"
      query_params = {"search": "*"+table_name+"*"}
    else:
      path = "api/v01/" + table_name + ".def.sdmx.json?"
      query_params = {}

    data = self.__fetch_json(path, query_params)

    # return empty if no useful metadata returned (likely table doesnt exist)
    if not data["structure"]["keyfamilies"]:
      return {}

    # this is the nomis internal table name
    table = data["structure"]["keyfamilies"]["keyfamily"][0]["id"]

    rawfields = data["structure"]["keyfamilies"]["keyfamily"][0]["components"]["dimension"]
    fields: dict[str, Any] = {}
    for rawfield in rawfields:
      field = rawfield["conceptref"]

      fields[field] = {}

      # ignore when too many categories (i.e. geograpical ones)
      if field.upper() == "CURRENTLY_RESIDING_IN" or field.upper() == "PLACE_OF_WORK":
        continue

      # further query to get categories
      path = "api/v01/dataset/"+table+"/"+field+".def.sdmx.json?"
      #print(path)

      try:
        fdata = self.__fetch_json(path, {})
      except timeout:
        print("HTTP timeout requesting metadata for " + table_name)
        return {}
      except (HTTPError, URLError):
        print("HTTP error requesting metadata for " + table_name)
        return {}
      else:
        values = fdata["structure"]["codelists"]["codelist"][0]["code"]
        #print(field+":")
        for value in values:
          # KEYs are stored as strings for json compatibility
          fields[field][value["value"]] = value["description"]["value"]

    # Fetch the geographies available for this table
    geogs = {}
    path = f"api/v01/dataset/{table}/geography/TYPE.def.sdmx.json?"
    try:
      fdata = self.__fetch_json(path, {})
    except timeout:
      print("HTTP timeout requesting geography metadata for " + table_name)
    except (HTTPError, URLError):
      print("HTTP error requesting geography metadata for " + table_name)
    else:
      if fdata["structure"]["codelists"]:
        values = fdata["structure"]["codelists"]["codelist"][0]["code"]
        #print(values)
        for value in values:
          geogs[str(value["value"])] = value["description"]["value"]

    result = {"nomis_table": table,
              "description": data["structure"]["keyfamilies"]["keyfamily"][0]["name"]["value"],
              "fields": fields,
              "geographies": geogs}

    # save a copy
    self.write_metadata(table_name, result)

    return result

  # loads metadata from cached json if available, otherwises downloads from nomisweb.
  # NB category KEYs need to be converted from string to integer for this data to work properly, see convert_code
  def load_metadata(self, table_name: str) -> dict[str, Any]:
    """Retrieves cached, or downloads census table metadata. Use this in preference to get_metadata.
    Args:
      table_name: the (ONS) table name, e.g. KS4402EW
    Returns:
      a dictionary containing information about the table contents including categories and category values.
    """
    filename = self.cache_dir / (table_name + "_metadata.json")
    # if file not there, get from nomisweb
    if not os.path.isfile(str(filename)):
      if self.verbose:
        print(filename, "not found, downloading...")
      return self.get_metadata(table_name)
    else:
      if self.verbose:
        print(filename, "found, using cached metadata...")
      with open(str(filename)) as metafile:
        meta = json.load(metafile)

    return meta

# private

  # download and cache the nomis codes for local authorities
  def __cache_lad_codes(self) -> dict[str, Any]:

    filename = self.cache_dir / "lad_codes.json"

    if not os.path.isfile(str(filename)):
      if self.verbose: print(filename, "not found, downloading LAD codes...")

      data = self.__fetch_json("api/v01/dataset/NM_144_1/geography/" \
          + str(Nomisweb.GEOCODE_LOOKUP["EnglandWales"]) + Nomisweb.GEOCODE_LOOKUP["LAD"] + ".def.sdmx.json?", {})
      if not data:
        return {}

      rawfields = data["structure"]["codelists"]["codelist"][0]["code"]
      codes = {}
      for rawfield in rawfields:
        codes[rawfield["description"]["value"]] = rawfield["value"]
        codes[rawfield["annotations"]["annotation"][2]["annotationtext"]] = rawfield["value"]
      if self.verbose: print("Writing LAD codes to ", filename)

      # save LAD codes
      with open(str(filename), "w") as metafile:
        json.dump(codes, metafile, indent=2)

    else:
      if self.verbose: print("using cached LAD codes:", filename)
      with open(str(filename)) as cached_ladcodes:
        codes = json.load(cached_ladcodes)
    return codes

  # given a list of integer codes, generates a string using the nomisweb shortened form
  # (consecutive numbers represented by a range, non-consecutive are comma separated
  def __fetch_json(self, path: str, query_params: dict[str, Any]) -> dict[str, Any]:
    # add API KEY to params
    query_params["uid"] = self.key

    query_string = Nomisweb.URL + path + str(urlencode(query_params))

    reply = {}
    try:
      response = request.urlopen(query_string, timeout=Nomisweb.TIMEOUT)
    except (HTTPError, URLError) as error:
      print('ERROR: ', error, '\n', query_string)
    except timeout:
      print('ERROR: request timed out\n', query_string)
    else:
      reply = json.loads(response.read().decode("utf-8"))
    return reply

  # save metadata as JSON for future reference
  def write_metadata(self, table: str, meta: dict[str, Any]) -> None:
    """method.
    Args:
        table: name of table
        meta: the metadata
        ...
    Returns:
        nothing.
    """

    filename = self.cache_dir / (table + "_metadata.json")
    if self.verbose: print("Writing metadata to ", str(filename))
    with open(str(filename), "w") as metafile:
      json.dump(meta, metafile, indent=2)

  # append <column> numeric values with the string values from the metadata
  # NB the "numeric" values are stored as strings in both the table and the metadata
  # this doesnt need to be a member
  def contextify(self, table_name: str, column: str, table: pd.DataFrame) -> None:
    """Adds context to a column in a table, as a separate column containing the meanings of each numerical value
    Args:
        table_name: name of census table
        column: name of column within the table (containing numeric values)
        table:
    Returns:
        a new table containing an extra column with descriptions of the numeric values.
    """

    metadata = self.load_metadata(table_name)

    if column not in metadata["fields"]:
      print(column, " is not in metadata")
      return
    if column not in table.columns:
      print(column, " is not in table")
      return

    # convert KEYs on the fly to integers (if they've been loaded from json they will be strings)
    lookup = {int(k): v for k, v in metadata["fields"][column].items()}
    table[column + "_NAME"] = table[column].map(lookup)


@lru_cache(maxsize=1)
def api_ew(*, cache_dir: Optional[str]=None, verbose: bool=False) -> Nomisweb:
  return Nomisweb(cache_dir=cache_dir, verbose=verbose)