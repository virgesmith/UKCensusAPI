"""
Data scraper for Scottish 2011 census Data
"""

import os.path
from pathlib import Path
import urllib.parse
import zipfile
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

  def get_metadata(self, table, resolution):
    z = zipfile.ZipFile(str(self.__source_to_zip(NRScotland.data_sources[NRScotland.GeoCodeLookup[resolution]])))
    #print(z.namelist())   
    raw_data = pd.read_csv(z.open(table + ".csv"))
    # assumes:
    # - first column is geography (unnamed)
    # - any subsequent columns are categorical
    # - named columns are categories   
    raw_cols = raw_data.columns.tolist()

    fields = {}

    col_index = 1
    while raw_cols[col_index][:8] == "Unnamed:":
      fields[table + "_" + str(col_index) + "_CODE"] = raw_data[raw_cols[col_index]].unique()
      col_index = col_index + 1

    fields[table + "_0_CODE"] = raw_data.columns.tolist()[col_index:]

    meta = { "table": table,
             "description": "",
             "geography": resolution,
             "fields": fields
          }
    return (meta, raw_data)
    #print(data.head())

  def get_data(self, table, resolution, geography, category_filter=None):

    meta, raw_data = self.get_metadata(table, resolution)
    raw_data = raw_data.replace("-", 0)
    # assumes the first n are (unnamed) columns we don't want to melt, geography coming first: n = geog + num categories - 1 (the one to melt) 
    lookup = raw_data.columns.tolist()[len(meta["fields"]):]

    #print(meta["fields"].keys())

    id_vars = ["GEOGRAPHY_CODE"]
    for i in range(1,len(meta["fields"])):
      id_vars.append(table + "_" + str(i) + "_CODE")
    cols = id_vars.copy()
    cols.extend(list(range(0,len(lookup))))
    # print(id_vars)
    # print(cols)

    raw_data.columns = cols
    raw_data = raw_data.melt(id_vars=id_vars)
    id_vars.extend([table + "_0_CODE", "OBS_VALUE"])
    raw_data.columns = id_vars

    # convert categories to numeric values
    for i in range(1,len(meta["fields"])):
      category_name = raw_data.columns[i]
      category_values = meta["fields"][category_name]
      # make sure metadata has same no. of categories
      assert len(category_values) == len(raw_data[category_name].unique())
      category_map = { k: v for v, k in enumerate(category_values)} 
      raw_data[category_name] = raw_data[category_name].map(category_map)

#    print(category_map)

    # geography (and category_filter) must be lists
    if isinstance(geography, str):
      geography = [geography]
    
    # TODO multi-category filters
    # if no category_filter is provided we return all categories
    # if category_filter is None:
    #   category_filter = raw_data[table + "_0_CODE"].unique()
    # if isinstance(category_filter, int):
    #   category_filter = [category_filter]

    # # filter by geography and category
    # return raw_data[(raw_data.GEOGRAPHY_CODE.isin(geography)) & (raw_data[table + "_CODE"].isin(category_filter))].reset_index(drop=True)
    return raw_data[raw_data.GEOGRAPHY_CODE.isin(geography)].reset_index(drop=True)

  # TODO this is very close to duplicating the code in Nomisweb.py - refactor
  def contextify(self, table, meta, colname):
    """
    Replaces the numeric category codes with the descriptive strings from the metadata
    """
    lookup = meta["fields"][colname]
    # convert list into dict keyed on list index
    mapping = { k: v for k, v in enumerate(lookup)} 
    category_name = colname.replace("_CODE", "_NAME")

    table[category_name] = table[colname].map(mapping)

    return table

  def __source_to_zip(self, source_name):
    """
    Downloads if necessary and returns the name of the locally cached zip file of the source data (replacing spaces with _)
    """
    zip = self.cache_dir / (source_name.replace(" ", "_") + ".zip")
    if not os.path.isfile(str(zip)):
      # The URL must have %20 (not "+") for space
      scotland_src = NRScotland.URL + "?downloadFileIds=" + urllib.parse.quote(source_name)
      print(scotland_src, " -> ", self.cache_dir / zip, "...", end="")
      response = requests.get(scotland_src)
      with open(str(zip), 'wb') as fd:
        for chunk in response.iter_content(chunk_size=1024):
          fd.write(chunk)
      print("OK")
    return zip

