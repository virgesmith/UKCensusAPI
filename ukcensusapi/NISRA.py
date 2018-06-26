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

class NISRA:
  """
  http://www.ninis2.nisra.gov.uk/Download/Census%202011/Detailed%20Characteristics%20Tables%20(statistical%20geographies).zip
  http://www.ninis2.nisra.gov.uk/Download/Census%202011/Key%20Statistics%20Tables%20(statistical%20geographies).zip
  http://www.ninis2.nisra.gov.uk/Download/Census%202011/Local%20Characteristic%20Tables%20(statistical%20geographies).zip
  http://www.ninis2.nisra.gov.uk/Download/Census%202011/Quick%20Statistics%20Tables%20(statistical%20geographies).zip
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
    "LAD": 0 # LGD
    "MSOA11": 1, # WARD
    "LSOA11": 2, # SOA
    "OA11": 3 # SA
  }

  NIGeoCodes = [ "LGD", "WARD", "SOA", "SA" ]

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

    # download the lookup if not present
    lookup_file = self.cache_dir / "ni_lookup.csv"
    if not os.path.isfile(str(lookup_file)):
      z = zipfile.ZipFile(str(self.__source_to_zip(NISRA.data_sources[2])))
      area_lookup = pd.read_csv(z.open("All_Geographies_Code_Files/NI_HIERARCHY.csv"))
      # TODO use a map (just in case col order changes)
      #self.area_lookup.columns = ["OA11", "LSOA11", "MSOA11", "LAD"]
      area_lookup.to_csv(str(lookup_file), index=False)

    self.area_lookup = pd.read_csv(str(lookup_file))
    
    #pd.read_csv(str(self.cache_dir / "sc_lookup.csv"))

    # TODO use a map (just in case col order changes)
    #self.area_lookup.columns = ["OA11", "LSOA11", "MSOA11", "LAD"]


  # TODO this could be merged with the Scottish version
  def __source_to_zip(self, source_name):
    """
    Downloads if necessary and returns the name of the locally cached zip file of the source data (replacing spaces with _)
    """
    zip = self.cache_dir / source_name.replace(" ", "_")
    print(zip)
    if not os.path.isfile(str(zip)):
      # The URL must have %20 for space (only)
      ni_src = NISRA.URL + source_name.replace(" ", "%20")
      print(ni_src, " -> ", self.cache_dir / zip, "...", end="")
      response = requests.get(ni_src)
      with open(str(zip), 'wb') as fd:
        for chunk in response.iter_content(chunk_size=1024):
          fd.write(chunk)
      print("OK")
    return zip
