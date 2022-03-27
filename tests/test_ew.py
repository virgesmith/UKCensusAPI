""" Test harness """

import os
from random import sample
import numpy as np
import sys
import pytest

from ukcensusapi.nomisweb import Nomisweb, _shorten
from ukcensusapi.query import Query #, NRScotland as Api_SC, NISRA as Api_NI, Query as Census


def test_get_lad_codes(api_ew):
  assert api_ew.get_lad_codes("Royston Vasey") == []
  assert api_ew.get_lad_codes("Leeds") == [1946157127]
  assert api_ew.get_lad_codes(["Leeds", "Bradford"]) == [1946157127, 1946157124]


# This overlaps test_getGeographyFromCodes
def test_geo_codes_ew(api_ew):
  result = api_ew.get_geo_codes([api_ew.GEOCODE_LOOKUP["EnglandWales"]], api_ew.GEOCODE_LOOKUP["LAD"])
  assert result == '1946157057...1946157404'
  result = api_ew.get_geo_codes([1946157127], api_ew.GEOCODE_LOOKUP["OA11"])
  assert result == '1254151943...1254154269,1254258198...1254258221,1254261711...1254261745,1254261853...1254261870,1254261894...1254261918,1254262125...1254262142,1254262341...1254262353,1254262394...1254262398,1254262498...1254262532,1254262620...1254262658,1254262922...1254262925'
  # test 2001 codes
  result = api_ew.get_geo_codes([1946157127], api_ew.GEOCODE_LOOKUP["MSOA01"])
  assert result == '1279265050...1279265157'


def test_get_metadata_ew(api_ew):
  meta = api_ew.get_metadata("NONEXISTENT")
  assert not meta
  meta = api_ew.get_metadata("KS401EW")
  assert meta["description"] == 'KS401EW - Dwellings, household spaces and accommodation type'
  assert meta["nomis_table"] == 'NM_618_1'
  # test 2001 table
  meta = api_ew.get_metadata("UV070")
  assert meta["description"] == 'UV070 - Communal Establishments'
  assert meta["nomis_table"] == 'NM_1686_1'


def test_get_url(api_ew):
  table = "NM_618_1"
  query_params = {
    "CELL": "7...13",
    "date": "latest",
    "RURAL_URBAN": "0",
    "select": "GEOGRAPHY_CODE,CELL,OBS_VALUE",
    "geography": "1245710558...1245710660,1245714998...1245714998,1245715007...1245715007,1245715021...1245715022",
    "MEASURES": "20100"
  }
  assert api_ew.get_url(table, query_params) == "https://www.nomisweb.co.uk/api/v01/dataset/NM_618_1.data.tsv?CELL=7...13&MEASURES=20100&RURAL_URBAN=0&date=latest&geography=1245710558...1245710660%2C1245714998...1245714998%2C1245715007...1245715007%2C1245715021...1245715022&select=GEOGRAPHY_CODE%2CCELL%2COBS_VALUE"


def test_get_data_ew(api_ew):
  table_name = "KS401EW"
#    table_internal = "NM_618_1"
  query_params = {
    "CELL": "7...13",
    "date": "latest",
    "RURAL_URBAN": "0",
    "select": "GEOGRAPHY_CODE,CELL,OBS_VALUE",
    "geography": "1245710558...1245710560",
    "MEASURES": "20100"
  }
  table = api_ew.get_data(table_name, query_params)
  assert table.shape == (21, 3)
  assert sum(table.OBS_VALUE) == 8214


#'table': 'QS202NI', 'description': '', 'geography': 'SOA', 'fields': {'QS202NI_0_CODE': {0: 'All Household Reference Persons (HRPs)', 1: 'Ethnic group of HRP: Black', 2: 'Ethnic group of HRP: Chinese', 3: 'Ethnic group of HRP: Mixed', 4: 'Ethnic group of HRP: Other', 5: 'Ethnic group of HRP: Other Asian', 6: 'Ethnic group of HRP: White'}}}

# OD data is structured differently
def test_get_od_data(api_ew):
  table = "WF01BEW"
#    table_internal = "NM_1228_1"
  query_params = {
    "date": "latest",
    "select": "currently_residing_in_code,place_of_work_code,OBS_VALUE",
    # OD are 5 LSOAs in central Leeds
    "currently_residing_in": "1249934756...1249934758,1249934760,1249934761",
    "place_of_work": "1249934756...1249934758,1249934760,1249934761",
    "MEASURES": "20100"
  }
  table = api_ew.get_data(table, query_params)
  assert table.shape == (25, 3)
  assert sum(table.OBS_VALUE) == 1791


# Projection data doesnt explicitly have a table name - tests directly specifying nomis internal name
def test_get_proj_data(api_ew):
  table_internal = "NM_2002_1"
  query_params = {
    "gender": "1,2",
    "c_age": "101...191",
    "MEASURES": "20100",
    "select": "geography_code,gender,c_age,obs_value",
    "geography": "1879048193...1879048194",
    "date": "latestMINUS15" # 2003
  }

  table = api_ew.get_data(table_internal, query_params)
  assert table.shape == (364, 4)
  assert sum(table.OBS_VALUE) == 597505


def test_get_and_add_descriptive_column(api_ew):

  table_name = "KS401EW"

  query_params = {
    "CELL": "7...13",
    "date": "latest",
    "RURAL_URBAN": "0",
    "select": "GEOGRAPHY_CODE,CELL,OBS_VALUE",
    "geography": "1245710558...1245710560",
    "MEASURES": "20100"
  }
  table = api_ew.get_data(table_name, query_params)
  assert table.shape == (21, 3)
  assert sum(table.OBS_VALUE) == 8214

  # first ensure table is unmodified if column doesnt exist
  old_cols = len(table.columns)
  api_ew.contextify(table_name, "NOT_THERE", table)
  assert len(table.columns) == old_cols

  api_ew.contextify(table_name, "CELL", table)

  assert table.at[0, "CELL_NAME"] == "Whole house or bungalow: Detached"
  assert table.at[1, "CELL_NAME"] == "Whole house or bungalow: Semi-detached"
  assert table.at[2, "CELL_NAME"] == "Whole house or bungalow: Terraced (including end-terrace)"
  assert table.at[3, "CELL_NAME"] == "Flat, maisonette or apartment: Purpose-built block of flats or tenement"
  assert table.at[4, "CELL_NAME"] == "Flat, maisonette or apartment: Part of a converted or shared house (including bed-sits)"
  assert table.at[5, "CELL_NAME"] == "Flat, maisonette or apartment: In a commercial building"
  assert table.at[6, "CELL_NAME"] == "Caravan or other mobile or temporary structure"


def test_get_geog_from_names():
  from conftest import TEST_CACHE_DIR
  query = Query(TEST_CACHE_DIR)

  result = query.get_geog_from_names(["Leeds"], Nomisweb.GEOCODE_LOOKUP["OA11"])
  assert result == '1254151943...1254154269,1254258198...1254258221,1254261711...1254261745,1254261853...1254261870,1254261894...1254261918,1254262125...1254262142,1254262341...1254262353,1254262394...1254262398,1254262498...1254262532,1254262620...1254262658,1254262922...1254262925'

  # same, but query with ONS code
  result = query.get_geog_from_names(["E08000035"], Nomisweb.GEOCODE_LOOKUP["OA11"])
  assert result == '1254151943...1254154269,1254258198...1254258221,1254261711...1254261745,1254261853...1254261870,1254261894...1254261918,1254262125...1254262142,1254262341...1254262353,1254262394...1254262398,1254262498...1254262532,1254262620...1254262658,1254262922...1254262925'

  result = query.get_geog_from_names(["Newcastle upon Tyne"], Nomisweb.GEOCODE_LOOKUP["LSOA11"])
  assert result == '1249910667...1249910832,1249935220...1249935228'

  result = query.get_geog_from_names(["Leeds", "Bradford"], Nomisweb.GEOCODE_LOOKUP["MSOA11"])
  assert result == '1245710411...1245710471,1245710558...1245710660,1245714998...1245714998,1245715007...1245715007,1245715021...1245715022'


def test_get_geog_from_codes():
  from conftest import TEST_CACHE_DIR
  query = Query(TEST_CACHE_DIR)
  result = query.api.get_geo_codes([Nomisweb.GEOCODE_LOOKUP["EnglandWales"]], Nomisweb.GEOCODE_LOOKUP["LAD"])
  assert result == '1946157057...1946157404'


# test example code
def test_geoquery():
  from conftest import TEST_CACHE_DIR
  import inst.examples.geoquery as eg_geo
  eg_geo.main(TEST_CACHE_DIR)


def test_contextify():
  from conftest import TEST_CACHE_DIR
  import inst.examples.contextify as eg_cont
  eg_cont.main(TEST_CACHE_DIR)


# just checks code snippet runs ok (i.e. returns 0)
def test_code_snippet():
  from conftest import TEST_CACHE_DIR
  query = Query(TEST_CACHE_DIR)

  if not sys.platform.startswith("win"):
    table = "KS401EW"
    meta = query.api.get_metadata(table)
    query_params = {
      "CELL": "7...13",
      "date": "latest",
      "RURAL_URBAN": "0",
      "select": "GEOGRAPHY_CODE,CELL,OBS_VALUE",
      "geography": "1245710558...1245710560",
      "MEASURES": "20100"
    }

    query.write_code_snippets(table, meta, query_params)
    assert os.system(f"python {query.api.cache_dir / (table + '.py')}") == 0


# checks the logic to compress a list of nomis geo codes into a shorter form for url
def test_shorten_codelist():
  n = list(range(1,21))

  for _ in range(0,100):
    short = _shorten(sample(n, len(n)))
    assert short == "1...20"

  del(n[3])
  for _ in range(0,100):
    short = _shorten(sample(n, len(n)))
    assert short == "1...3,5...20"

  del(n[16])
  for _ in range(0,100):
    short = _shorten(sample(n, len(n)))
    assert short == "1...3,5...17,19...20"

  del(n[16])
  for _ in range(0,100):
    short = _shorten(sample(n, len(n)))
    assert short == "1...3,5...17,20"
