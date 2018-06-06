"""
Data scraper for Scottish 2011 census Data
"""

import os.path
from pathlib import Path
import json
import urllib.parse
import zipfile
import numpy as np
import pandas as pd
import requests

import ukcensusapi.utils as utils

# Geographical area (EW equivalents)
# Council area (LAD)
# Intermediate zone (MSOA) ??
# Data zone (LSOA)
# Output area

class NRScotland:
  """
  NRScotland web data scraper.
  """

#   ['S92000003' Scotland
#   Council areas: 'S12000005' 'S12000006' 'S12000008' 'S12000010' 'S12000011'
#   'S12000013' 'S12000014' 'S12000015' 'S12000017' 'S12000018' 'S12000019'
#  'S12000020' 'S12000021' 'S12000023' 'S12000024' 'S12000026' 'S12000027'
#  'S12000028' 'S12000029' 'S12000030' 'S12000033' 'S12000034' 'S12000035'
#  'S12000036' 'S12000038' 'S12000039' 'S12000040' 'S12000041' 'S12000042'
#  'S12000044' 'S12000045' 'S12000046']

  # static constants
  URL = "http://www.scotlandscensus.gov.uk/ods-web/download/getDownloadFile.html"

  # timeout for http requests
  Timeout = 15

  data_sources = ["Council Area blk", "SNS Data Zone 2011 blk", "Output Area blk"]

  GeoCodeLookup = {
    # give meaning to some common nomis geography types/codes
    "LAD": 0, #"Council Area blk", , 
    # MSOA (intermediate zone)?
    "LSOA11": 1, #"SNS Data Zone 2011 blk"
    "OA11": 2, #"Output Area blk"
  }

  # initialise, supplying a location to cache downloads
  def __init__(self, cache_dir):
    """Constructor.
    Args:
        cache_dir: cache directory
    Returns:
        an instance.
    """
    # checks exists and is writable, creates if necessary
    self.cache_dir = utils.init_cache_dir(cache_dir)

#    for data_source in NRScotland.data_sources:
#      zipfile = self.__source_to_zip(data_source)

  def get_metadata(self, table, resolution):
    z = zipfile.ZipFile(self.__source_to_zip(NRScotland.data_sources[NRScotland.GeoCodeLookup[resolution]]))
    #print(z.namelist())   
    data = pd.read_csv(z.open(table + ".csv"))  
    # assumes first column is geography (unnamed)   
    meta = { "table": table,
             "description": "",
             "geography": resolution,
             "fields": { table + "_CODE": data.columns.tolist()[1:] }
          }
    return meta
    #print(data.head())

  def get_data(self, table, resolution, geography, category_filter=None):

    z = zipfile.ZipFile(self.__source_to_zip(NRScotland.data_sources[NRScotland.GeoCodeLookup[resolution]]))
    data = pd.read_csv(z.open(table + ".csv"))  
    data = data.replace("-", 0)
    # assumes first column is geography (unnamed)   
    lookup = data.columns.tolist()[1:]
    # we are allowed a list of mixed types (str/int) and these are valid col names
    cols = list(range(0,len(lookup)))
    cols.insert(0, "GEOGRAPHY_CODE")

    data.columns = cols
    data = data.melt(id_vars=["GEOGRAPHY_CODE"])
    data.columns = ["GEOGRAPHY_CODE", table + "_CODE", "OBS_VALUE"]

    # geography (and category_filter) must be lists
    if isinstance(geography, str):
      geography = [geography]
    # if no category_filter is provided we return all categories
    if category_filter is None:
      category_filter = data[table + "_CODE"].unique()
    if isinstance(category_filter, int):
      category_filter = [category_filter]

    # filter by geography and category
    return data[(data.GEOGRAPHY_CODE.isin(geography)) & (data[table + "_CODE"].isin(category_filter))].reset_index(drop=True)

  # TODO this is very close to duplicating the code in Nomisweb.py - refactor
  def contextify(self, table, meta):
    """
    Replaces the numeric category codes with the descriptive strings from the metadata
    """
    lookup = meta["fields"]
    for category_code in lookup:
      # convert list into dict keyed on list index
      mapping = { k: v for k, v in enumerate((lookup[category_code]))} 
      category_name = category_code.replace("_CODE", "_NAME")
      table[category_name] = table[category_code].map(mapping)

    return table


  def __source_to_zip(self, source_name):
    """
    Downloads if necessary and returns the name of the locally cached zip file of the source data (replacing spaces with _)
    """
    zipfile = self.cache_dir / (source_name.replace(" ", "_") + ".zip")
    if not os.path.isfile(zipfile):
      # The URL must have %20 (not "+") for space
      scotland_src = NRScotland.URL + "?downloadFileIds=" + urllib.parse.quote(source_name)
      print(scotland_src, " -> ", self.cache_dir / zipfile, "...", end="")
      response = requests.get(scotland_src)
      with open(zipfile, 'wb') as fd:
        for chunk in response.iter_content(chunk_size=1024):
          fd.write(chunk)
      print("OK")
    return zipfile

