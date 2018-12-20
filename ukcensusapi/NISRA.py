"""
Northern Ireland
"""

import os.path
from pathlib import Path
import urllib.parse
import zipfile
import pandas as pd
import requests

import ukcensusapi.utils as utils

# assumes all areas in coverage are the same type
def _coverage_type(code):
  if isinstance(code, list):
    code = code[0]
  if code == "N92000002":
    return "ALL"
  # TODO regex?
  elif len(code) == 4: # e.g. 95AA
    return "LGD"
  elif len(code) == 6: # e.g. 95AA01 (ward)
    return "WARD"
  elif len(code) == 8: # e.g. 95AA01S1
    return "SOA"
  elif code[:3] == "N00":
    return "OA"
  else:
    raise ValueError("Invalid code: {}".format(code))

class NISRA:
  """
  Scrapes and refomats NI 2011 census data from NISRA website
  """
  # static constants
  URL = "http://www.ninis2.nisra.gov.uk/Download/Census%202011/"

  # timeout for http requests
  Timeout = 15

  data_sources = ["Detailed Characteristics Tables (statistical geographies).zip", 
                  "Key Statistics Tables (statistical geographies).zip",
                  "Local Characteristic Tables (statistical geographies).zip", # note slight inconsistency in name
                  "Quick Statistics Tables (statistical geographies).zip"]

  GeoCodeLookup = {
    "LAD": 0, # LGD
    "MSOA11": 1, # WARD
    "LSOA11": 2, # SOA
    "OA11": 3 # SA
  }

  NIGeoCodes = [ "LGD", "WARD", "SOA", "SA" ]

  source_map = { "LC": 2, "DC": 0, "KS": 1, "QS": 3 } 

  res_map = { "SA": "SMALL AREAS", "SOA": "SUPER OUTPUT AREAS"}

  LADs = {
    "95AA":	"Antrim",
    "95BB":	"Ards",
    "95CC":	"Armagh",
    "95DD":	"Ballymena",
    "95EE":	"Ballymoney",
    "95FF":	"Banbridge",
    "95GG":	"Belfast",
    "95HH":	"Carrickfergus",
    "95II":	"Castlereagh",
    "95JJ":	"Coleraine",
    "95KK":	"Cookstown",
    "95LL":	"Craigavon",
    "95MM":	"Derry",
    "95NN":	"Down",
    "95OO":	"Dungannon",
    "95PP":	"Fermanagh",
    "95QQ":	"Larne",
    "95RR":	"Limavady",
    "95SS":	"Lisburn",
    "95TT":	"Magherafelt",
    "95UU":	"Moyle",
    "95VV":	"Newry and Mourne",
    "95WW":	"Newtownabbey",
    "95XX":	"North Down",
    "95YY":	"Omagh",
    "95ZZ":	"Strabane" 
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

    self.offline_mode = not utils.check_online(self.URL)
    if self.offline_mode:
      print("Unable to contact %s, operating in offline mode - pre-cached data only" % self.URL)

    # download the lookup if not present
    lookup_file = self.cache_dir / "ni_lookup.csv"
    if not os.path.isfile(str(lookup_file)):
      z = zipfile.ZipFile(str(self.__source_to_zip(NISRA.data_sources[2])))
      pd.read_csv(z.open("All_Geographies_Code_Files/NI_HIERARCHY.csv")) \
        .drop(["NUTS3","HSCT","ELB","COUNTRY"], axis=1) \
        .to_csv(str(lookup_file), index=False)

    # load the area lookup
    self.area_lookup = pd.read_csv(str(lookup_file))

  # TODO this is very close to duplicating the code in NRScotland.py - refactor?
  def get_geog(self, coverage, resolution):
    """
    Returns all areas at resolution in coverage
    """

    resolution = _ni_resolution(resolution)

    # assumes all areas in coverage are the same type
    coverage_type = _coverage_type(coverage)
    if coverage_type == "ALL":
      return self.area_lookup[resolution].unique()

    # ensure list
    if isinstance(coverage, str):
      coverage = [coverage]

    return self.area_lookup[self.area_lookup[coverage_type].isin(coverage)][resolution].unique()

  def get_metadata(self, table, resolution):
    return self.__get_metadata_impl(table, resolution)[0]

  def __get_metadata_impl(self, table, resolution):

    resolution = _ni_resolution(resolution)

    # If request at LGD/WARD level we will need to aggregate finer data
    if resolution == "LGD" or resolution == "WARD":
      resolution = "SOA"

    z = zipfile.ZipFile(str(self.__source_to_zip(NISRA.data_sources[NISRA.source_map[table[:2]]])))
    raw_meta = pd.read_csv(z.open(NISRA.res_map[resolution]+"/"+table+"DESC0.CSV")) \
                 .drop(["ColumnVariableMeasurementUnit", "ColumnVariableStatisticalUnit"], axis=1)
    # if every field has the same number of commas we split, otherwise assume number of categories
    # is the minimum. Warn that category names may be messed up 
    commas = raw_meta["ColumnVariableDescription"].str.count(",").unique()
    min_categories = min(commas)
    if len(commas) > 1 and min_categories > 0:
      print("WARNING: it appears that {} is multivariate and some category descriptions contain a comma. ".format(table) + \
            "This makes the individual category names ambiguous. Be aware that category names may have been be incorrectly interpreted.")

    # str.split interprets 0 as split on all instances
    if min_categories > 0:
      raw_meta = pd.concat([raw_meta["ColumnVariableCode"], raw_meta["ColumnVariableDescription"].str.split(", ", n=min_categories, expand=True)], axis=1)
    else:
      raw_meta.rename({"ColumnVariableDescription": 0}, axis=1, inplace=True)

    #raw_meta['ColumnVariableCode'] = raw_meta['ColumnVariableCode'].map(lambda x: int(x[-4:]))
    raw_meta = raw_meta.set_index("ColumnVariableCode", drop=True) 

    meta = { "table": table,
             "description": "",
             "geography": resolution,
             "fields": {} }

    text_columns = range(0,len(raw_meta.columns)) 
    for text_column in text_columns:
      raw_meta[text_column] = raw_meta[text_column].astype("category")
      code_column = table + "_" + str(text_column) + "_CODE"
      raw_meta[code_column] = raw_meta[text_column].cat.codes
      meta["fields"][code_column] = dict(enumerate(raw_meta[text_column].cat.categories))

    # now remove text columns
    raw_meta.drop(text_columns, axis=1, inplace=True)

    return (meta, raw_meta)

  def get_data(self, table, region, resolution, category_filters={}, r_compat=False):

    resolution = _ni_resolution(resolution)

    # No data is available for Ward/LGD (~MSOA/LAD) so we get SOA (LSOA) then aggregate
    agg_workaround = False
    if resolution == "LGD" or resolution == "WARD":
      agg_workaround = True
      actual_resolution = resolution
      resolution = "SOA"

    (meta, raw_meta) = self.__get_metadata_impl(table, resolution)

    area_codes = self.get_geog(region, resolution)

    z = zipfile.ZipFile(str(self.__source_to_zip(NISRA.data_sources[NISRA.source_map[table[:2]]])))
    id_vars = ["GeographyCode"]
    raw_data = pd.read_csv(z.open(NISRA.res_map[resolution]+"/"+table+"DATA0.CSV")) \
                 .melt(id_vars=id_vars)
    raw_data.columns = ["GEOGRAPHY_CODE", table, "OBS_VALUE"]

    # Filter by region
    raw_data = raw_data[raw_data["GEOGRAPHY_CODE"].isin(area_codes)]

    # join with raw metadata and drop the combo code
    data = raw_data.join(raw_meta, on=table).drop([table], axis=1)

    # If we actually requested MSOA-level data, aggregrate the LSOAs within each MSOA
    if agg_workaround:
      data = data.reset_index(drop=True)
      lookup = self.area_lookup[self.area_lookup[resolution].isin(data.GEOGRAPHY_CODE)]
      lookup = pd.Series(lookup[actual_resolution].values, index=lookup[resolution]).to_dict()
      data.GEOGRAPHY_CODE = data.GEOGRAPHY_CODE.map(lookup)
      cols = list(data.columns)
      # remove acts in-place and has no return value so can't chain it 
      cols.remove("OBS_VALUE")
      data = data.groupby(cols).sum().reset_index()

    # Filter by category
    for category in category_filters:
      filter = category_filters[category]
      if isinstance(filter, int):
        filter = [filter]
      data = data[data[category].isin(filter)]

    # for R (which doesnt understand a pandas dataframe), we return np.arrays
    data.reset_index(drop=True, inplace=True)
    if r_compat:
      return {"columns": data.columns.values, "values": data.values}
    else:
      return data

  # TODO this is very close to duplicating the code in Nomisweb.py/NRScotland.py - refactor
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

  # TODO this could be merged with the Scottish version
  def __source_to_zip(self, source_name):
    """
    Downloads if necessary and returns the name of the locally cached zip file of the source data (replacing spaces with _)
    """
    zipfile = self.cache_dir / source_name.replace(" ", "_")
    if not os.path.isfile(str(zipfile)):
      # The URL must have %20 for space (only)
      ni_src = NISRA.URL + source_name.replace(" ", "%20")
      print(ni_src, " -> ", zipfile, "...", end="")
      response = requests.get(ni_src)
      response.raise_for_status()
      with open(str(zipfile), 'wb') as fd:
        for chunk in response.iter_content(chunk_size=1024):
          fd.write(chunk)
      print("OK")
    return zipfile

def _ni_resolution(resolution):
  """
  Maps E&W statistical geography codes to their closest NI equvalents
  """
  # check if already an NI code
  if resolution in NISRA.NIGeoCodes:
    return resolution

  if not resolution in NISRA.GeoCodeLookup:
    raise ValueError("resolution '{}' is not available".format(resolution))

  return NISRA.NIGeoCodes[NISRA.GeoCodeLookup[resolution]]

