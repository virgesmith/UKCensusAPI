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

# Geographical area (EW equivalents)
# Council area (LAD)
# Intermediate zone (MSOA) ??
# Data zone (LSOA)
# Output area

def _expand_home(path):
  """
  pathlib doesn't interpret ~/ as $HOME
  Doesnt deal with other user's homes e.g. ~another/dir is not changed
  """
  return Path(path.replace("~/", str(Path.home()) + "/"))


class NRScotland:
  """
  NRScotland web data scraper.
  """

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
    self.cache_dir = _expand_home(cache_dir)

    for data_source in NRScotland.data_sources:
      zipfile = self.__source_to_zip(data_source)
      if not os.path.isfile(zipfile):
        # The URL must have %20 (not "+") for space
        scotland_src = NRScotland.URL + "?downloadFileIds=" + urllib.parse.quote(data_source)
        print(scotland_src, " -> ", self.cache_dir / zipfile)
        response = requests.get(scotland_src)
        with open(zipfile, 'wb') as fd:
          for chunk in response.iter_content(chunk_size=1024):
            fd.write(chunk)

  def get_metadata(self, table, resolution):
    z = zipfile.ZipFile(self.__source_to_zip(NRScotland.data_sources[NRScotland.GeoCodeLookup[resolution]]))
    #print(z.namelist())   
    data = pd.read_csv(z.open(table + ".csv"))  
    # assumes first column is geography (unnamed)   
    return data.columns.tolist()[1:]
    #print(data.head())

  def get_data(self, table, resolution):
    z = zipfile.ZipFile(self.__source_to_zip(NRScotland.data_sources[NRScotland.GeoCodeLookup[resolution]]))
    data = pd.read_csv(z.open(table + ".csv"))  
    data = data.replace("-", 0)
    # assumes first column is geography (unnamed)   
    lookup = data.columns.tolist()[1:]
    cols = list(map(str, range(0,len(lookup))))
    cols.insert(0, "GEOGRAPHY_CODE")

    data.columns = cols
    print(data.head())
    data = data.melt(id_vars=["GEOGRAPHY_CODE"])
    data.columns = ["GEOGRAPHY_CODE", table + "_CATEGORY", "OBS_VALUE"]
    print(data.head())
    print(data.KS401SC_CATEGORY.unique())

  def __source_to_zip(self, source_name):
    """
    Returns the locally cached zip file of the source data (replacing spaces with _)
    """
    return self.cache_dir / (source_name.replace(" ", "_") + ".zip")

