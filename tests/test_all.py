""" Test harness """

# Disable "Line too long"
# pylint: disable=C0301

import os
from unittest import TestCase
from random import sample
import numpy as np

import ukcensusapi.Nomisweb as Api_EW
import ukcensusapi.NRScotland as Api_SC
import ukcensusapi.Query as Census

# test methods only run if prefixed with "test"
class Test(TestCase):
  """ Test harness """
  api_ew = Api_EW.Nomisweb("/tmp/UKCensusAPI")
  api_sc = Api_SC.NRScotland("/tmp/UKCensusAPI")
  query = Census.Query(api_ew)

  def test_get_lad_codes(self):
    self.assertTrue(self.api_ew.get_lad_codes("Royston Vasey") == [])
    self.assertTrue(self.api_ew.get_lad_codes("Leeds") == [1946157127])
    self.assertTrue(self.api_ew.get_lad_codes(["Leeds", "Bradford"]) == [1946157127, 1946157124])

  def test_cache_dir_invalid(self):
    self.assertRaises(PermissionError, Api_EW.Nomisweb, "/home/invalid")
    self.assertRaises(PermissionError, Api_SC.NRScotland, "/bin")
    self.assertRaises(PermissionError, Api_SC.NRScotland, "/bin/ls")

  # This overlaps test_getGeographyFromCodes
  def test_geo_codes(self):
    result = self.api_ew.get_geo_codes([Api_EW.Nomisweb.GeoCodeLookup["EnglandWales"]], Api_EW.Nomisweb.GeoCodeLookup["LAD"])
    self.assertEqual(result, '1946157057...1946157404')
    result = self.api_ew.get_geo_codes([1946157127], Api_EW.Nomisweb.GeoCodeLookup["OA11"])
    self.assertEqual(result, '1254151943...1254154269,1254258198...1254258221,1254261711...1254261745,1254261853...1254261870,1254261894...1254261918,1254262125...1254262142,1254262341...1254262353,1254262394...1254262398,1254262498...1254262532,1254262620...1254262658,1254262922...1254262925')
    # test 2001 codes
    result = self.api_ew.get_geo_codes([1946157127], Api_EW.Nomisweb.GeoCodeLookup["MSOA01"])
    self.assertEqual(result, '1279265050...1279265157')

    # Scotland
    lads = ['S12000033', 'S12000034', 'S12000041', 'S12000035', 'S12000026', 'S12000005',
            'S12000039', 'S12000006', 'S12000042', 'S12000008', 'S12000045', 'S12000010',
            'S12000011', 'S12000036', 'S12000014', 'S12000015', 'S12000046', 'S12000017',
            'S12000018', 'S12000019', 'S12000020', 'S12000021', 'S12000044', 'S12000023',
            'S12000024', 'S12000038', 'S12000027', 'S12000028', 'S12000029', 'S12000030',
            'S12000040', 'S12000013'].sort()

    msoa_ab = ['S02001275', 'S02001238', 'S02001237', 'S02001236', 'S02001278', 'S02001284',
               'S02001247', 'S02001249', 'S02001246', 'S02001250', 'S02001261', 'S02001252',
               'S02001251', 'S02001257', 'S02001258', 'S02001254', 'S02001256', 'S02001253',
               'S02001248', 'S02001242', 'S02001240', 'S02001241', 'S02001239', 'S02001243',
               'S02001259', 'S02001260', 'S02001264', 'S02001265', 'S02001268', 'S02001269',
               'S02001267', 'S02001274', 'S02001266', 'S02001263', 'S02001262', 'S02001245',
               'S02001270', 'S02001272', 'S02001273', 'S02001271', 'S02001244', 'S02001279',
               'S02001282', 'S02001281', 'S02001280', 'S02001276', 'S02001277', 'S02001283',
               'S02001255'].sort()

    result = self.api_sc.get_geog("S92000003", "LAD").sort()
    self.assertTrue(np.array_equal(result, lads))    
    result = self.api_sc.get_geog("S12000033", "MSOA11").sort()
    self.assertTrue(np.array_equal(result, msoa_ab))    
    result = self.api_sc.get_geog("S12000033", "LSOA11")
    self.assertTrue(len(result) == 283)    
    result = self.api_sc.get_geog("S12000033", "OA11")
    self.assertTrue(len(result) == 1992)    

  def test_get_metadata(self):
    meta = self.api_ew.get_metadata("NONEXISTENT")
    self.assertFalse(meta)
    meta = self.api_ew.get_metadata("KS401EW")
    self.assertEqual(meta["description"], 'KS401EW - Dwellings, household spaces and accommodation type')
    self.assertEqual(meta["nomis_table"], 'NM_618_1')
    # test 2001 table
    meta = self.api_ew.get_metadata("UV070")
    self.assertEqual(meta["description"], 'UV070 - Communal Establishments')
    self.assertEqual(meta["nomis_table"], 'NM_1686_1')

    meta = self.api_sc.get_metadata("KS401SC", "LAD")
    self.assertEqual(meta["table"], 'KS401SC')
    self.assertEqual(meta["geography"], 'LAD')
    self.assertTrue('KS401SC_0_CODE' in meta["fields"])

  def test_get_url(self):
    table = "NM_618_1"
    query_params = {}
    query_params["CELL"] = "7...13"
    query_params["date"] = "latest"
    query_params["RURAL_URBAN"] = "0"
    query_params["select"] = "GEOGRAPHY_CODE,CELL,OBS_VALUE"
    query_params["geography"] = "1245710558...1245710660,1245714998...1245714998,1245715007...1245715007,1245715021...1245715022"
    query_params["MEASURES"] = "20100"
    self.assertEqual(self.api_ew.get_url(table, query_params), "https://www.nomisweb.co.uk/api/v01/dataset/NM_618_1.data.tsv?CELL=7...13&MEASURES=20100&RURAL_URBAN=0&date=latest&geography=1245710558...1245710660%2C1245714998...1245714998%2C1245715007...1245715007%2C1245715021...1245715022&select=GEOGRAPHY_CODE%2CCELL%2COBS_VALUE")

  def test_get_data(self):
    table_name = "KS401EW"
#    table_internal = "NM_618_1"
    query_params = {}
    query_params["CELL"] = "7...13"
    query_params["date"] = "latest"
    query_params["RURAL_URBAN"] = "0"
    query_params["select"] = "GEOGRAPHY_CODE,CELL,OBS_VALUE"
    query_params["geography"] = "1245710558...1245710560"
    query_params["MEASURES"] = "20100"
    table = self.api_ew.get_data(table_name, query_params)
    self.assertEqual(table.shape, (21, 3))
    self.assertEqual(sum(table.OBS_VALUE), 8214)

    table_name = "KS401SC"
    geography = "S12000033" # Aberdeen
    categories = { "KS401SC_0_CODE": range(8,15) }
    table = self.api_sc.get_data(table_name, "LAD", geography, categories)
    self.assertEqual(table.shape, (7, 3))
    self.assertEqual(sum(table.OBS_VALUE), 108153)

    table_name = "DC2101SC"
    geography = "S12000033" # Aberdeen
    categories = { "DC2101SC_0_CODE": 4, # White Irish 
                   "DC2101SC_1_CODE": [1,2], # M+F
                   "DC2101SC_2_CODE": [6,7,8,9,10,11,12] } # 18-49
    table = self.api_sc.get_data(table_name, "LAD", geography, categories)
    self.assertEqual(table.shape, (14, 5))
    self.assertEqual(sum(table.OBS_VALUE), 1732)
    

  # OD data is structured differently
  def test_get_od_data(self):
    table = "WF01BEW"
#    table_internal = "NM_1228_1"
    query_params = {}
    query_params["date"] = "latest"
    query_params["select"] = "currently_residing_in_code,place_of_work_code,OBS_VALUE"
    # OD are 5 LSOAs in central Leeds
    query_params["currently_residing_in"] = "1249934756...1249934758,1249934760,1249934761"
    query_params["place_of_work"] = "1249934756...1249934758,1249934760,1249934761"
    query_params["MEASURES"] = "20100"
    table = self.api_ew.get_data(table, query_params)
    self.assertEqual(table.shape, (25, 3))
    self.assertEqual(sum(table.OBS_VALUE), 1791)

  # Projection data doesnt explicitly have a table name - tests directly specifying nomis internal name
  def test_get_proj_data(self):
    table_internal = "NM_2002_1"
    query_params = {
      "gender": "1,2",
      "c_age": "101...191",
      "MEASURES": "20100",
      "select": "geography_code,gender,c_age,obs_value",
      "geography": "1879048193...1879048194",
      "date": "latestMINUS15" # 2001
    }

    table = self.api_ew.get_data(table_internal, query_params)
    self.assertEqual(table.shape, (364, 4))
    self.assertEqual(sum(table.OBS_VALUE), 591572)   

  def test_get_and_add_descriptive_column(self):

    table_name = "KS401EW"

    query_params = {}
    query_params["CELL"] = "7...13"
    query_params["date"] = "latest"
    query_params["RURAL_URBAN"] = "0"
    query_params["select"] = "GEOGRAPHY_CODE,CELL,OBS_VALUE"
    query_params["geography"] = "1245710558...1245710560"
    query_params["MEASURES"] = "20100"
    table = self.api_ew.get_data(table_name, query_params)
    self.assertEqual(table.shape, (21, 3))
    self.assertEqual(sum(table.OBS_VALUE), 8214)

    # first ensure table is unmodified if column doesnt exist
    old_cols = len(table.columns)
    self.api_ew.contextify(table_name, "NOT_THERE", table)
    self.assertTrue(len(table.columns) == old_cols)

    self.api_ew.contextify(table_name, "CELL", table)

    self.assertTrue(table.at[0, "CELL_NAME"] == "Whole house or bungalow: Detached")
    self.assertTrue(table.at[1, "CELL_NAME"] == "Whole house or bungalow: Semi-detached")
    self.assertTrue(table.at[2, "CELL_NAME"] == "Whole house or bungalow: Terraced (including end-terrace)")
    self.assertTrue(table.at[3, "CELL_NAME"] == "Flat, maisonette or apartment: Purpose-built block of flats or tenement")
    self.assertTrue(table.at[4, "CELL_NAME"] == "Flat, maisonette or apartment: Part of a converted or shared house (including bed-sits)")
    self.assertTrue(table.at[5, "CELL_NAME"] == "Flat, maisonette or apartment: In a commercial building")
    self.assertTrue(table.at[6, "CELL_NAME"] == "Caravan or other mobile or temporary structure")

  def test_get_geog_from_names(self):
    result = self.query.get_geog_from_names(["Leeds"], Api_EW.Nomisweb.GeoCodeLookup["OA11"])
    self.assertEqual(result, '1254151943...1254154269,1254258198...1254258221,1254261711...1254261745,1254261853...1254261870,1254261894...1254261918,1254262125...1254262142,1254262341...1254262353,1254262394...1254262398,1254262498...1254262532,1254262620...1254262658,1254262922...1254262925')

    # same, but query with ONS code
    result = self.query.get_geog_from_names(["E08000035"], Api_EW.Nomisweb.GeoCodeLookup["OA11"])
    self.assertEqual(result, '1254151943...1254154269,1254258198...1254258221,1254261711...1254261745,1254261853...1254261870,1254261894...1254261918,1254262125...1254262142,1254262341...1254262353,1254262394...1254262398,1254262498...1254262532,1254262620...1254262658,1254262922...1254262925')

    result = self.query.get_geog_from_names(["Newcastle upon Tyne"], Api_EW.Nomisweb.GeoCodeLookup["LSOA11"])
    self.assertEqual(result, '1249910667...1249910832,1249935220...1249935228')

    result = self.query.get_geog_from_names(["Leeds", "Bradford"], Api_EW.Nomisweb.GeoCodeLookup["MSOA11"])
    self.assertEqual(result, '1245710411...1245710471,1245710558...1245710660,1245714998...1245714998,1245715007...1245715007,1245715021...1245715022')

  def test_get_geog_from_codes(self):
    result = self.query.api.get_geo_codes([Api_EW.Nomisweb.GeoCodeLookup["EnglandWales"]], Api_EW.Nomisweb.GeoCodeLookup["LAD"])
    self.assertEqual(result, '1946157057...1946157404')

  # test example code

  def test_geoquery(self):
    import inst.examples.geoquery as eg_geo
    eg_geo.main()

  def test_contextify(self):
    import inst.examples.contextify as eg_cont
    eg_cont.main()

  # just checks code snippet runs ok (i.e. returns 0)
  def test_code_snippet(self):
    table = "KS401EW"
    meta = self.api_ew.get_metadata(table)
    query_params = {}
    query_params["CELL"] = "7...13"
    query_params["date"] = "latest"
    query_params["RURAL_URBAN"] = "0"
    query_params["select"] = "GEOGRAPHY_CODE,CELL,OBS_VALUE"
    query_params["geography"] = "1245710558...1245710560"
    query_params["MEASURES"] = "20100"

    self.query.write_code_snippets(table, meta, query_params)
    self.assertTrue(os.system("python3 " + str(self.api_ew.cache_dir / (table + ".py"))) == 0)
    # fails on travis because R isnt installed
    #self.assertTrue(os.system("Rscript " + self.api.cache_dir + table + ".R") == 0)

  # checks the logic to compress a list of nomis geo codes into a shorter form for url
  def test_shorten_codelist(self):
    n = list(range(1,21))

    for _ in range(0,100):
      short = Api_EW._shorten(sample(n, len(n))) 
      self.assertEqual(short, "1...20")

    del(n[3])
    for _ in range(0,100):
      short = Api_EW._shorten(sample(n, len(n))) 
      self.assertEqual(short, "1...3,5...20")

    del(n[16])
    for _ in range(0,100):
      short = Api_EW._shorten(sample(n, len(n))) 
      self.assertEqual(short, "1...3,5...17,19...20")

    del(n[16])
    for _ in range(0,100):
      short = Api_EW._shorten(sample(n, len(n))) 
      self.assertEqual(short, "1...3,5...17,20")
