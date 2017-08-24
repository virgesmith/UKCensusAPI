
# Disable "Line too long"
# pylint: disable=C0301

import os
from unittest import TestCase

import ukcensusapi.Nomisweb as Api
import ukcensusapi.Query as Census

# test methods only run if prefixed with "test"
class Test(TestCase):
  api = Api.Nomisweb("/tmp/UKCensusAPI")
  query = Census.Query(api)

  def test_get_lad_codes(self):
    self.assertTrue(self.api.get_lad_codes("Royston Vasey") == [])
    self.assertTrue(self.api.get_lad_codes("Leeds") == [1946157127])
    self.assertTrue(self.api.get_lad_codes(["Leeds", "Bradford"]) == [1946157127, 1946157124])

  # This overlaps test_getGeographyFromCodes
  def test_geo_codes(self):
    result = self.api.get_geo_codes([Api.Nomisweb.EnglandWales], Api.Nomisweb.LAD)
    self.assertEqual(result, '1946157057...1946157404')
    result = self.api.get_geo_codes([1946157127], Api.Nomisweb.OA)
    self.assertEqual(result, '1254151943...1254154269,1254258198...1254258221,1254261711...1254261745,1254261853...1254261870,1254261894...1254261918,1254262125...1254262142,1254262341...1254262353,1254262394...1254262398,1254262498...1254262532,1254262620...1254262658,1254262922...1254262925')

  def test_get_metadata(self):
    meta = self.api.get_metadata("NONEXISTENT")
    self.assertFalse(meta)
    meta = self.api.get_metadata("KS401EW")
    self.assertEqual(meta["description"], 'KS401EW - Dwellings, household spaces and accommodation type')
    self.assertEqual(meta["nomis_table"], 'NM_618_1')

  def test_get_url(self):
    table = "NM_618_1"
    query_params = {}
    query_params["CELL"] = "7...13"
    query_params["date"] = "latest"
    query_params["RURAL_URBAN"] = "0"
    query_params["select"] = "GEOGRAPHY_CODE,CELL,OBS_VALUE"
    query_params["geography"] = "1245710558...1245710660,1245714998...1245714998,1245715007...1245715007,1245715021...1245715022"
    query_params["MEASURES"] = "20100"
    self.assertEqual(self.api.get_url(table, query_params), "https://www.nomisweb.co.uk/api/v01/dataset/NM_618_1.data.tsv?CELL=7...13&MEASURES=20100&RURAL_URBAN=0&date=latest&geography=1245710558...1245710660%2C1245714998...1245714998%2C1245715007...1245715007%2C1245715021...1245715022&select=GEOGRAPHY_CODE%2CCELL%2COBS_VALUE")

  def test_get_data(self):
    table = "KS401EW"
    table_internal = "NM_618_1"
    query_params = {}
    query_params["CELL"] = "7...13"
    query_params["date"] = "latest"
    query_params["RURAL_URBAN"] = "0"
    query_params["select"] = "GEOGRAPHY_CODE,CELL,OBS_VALUE"
    query_params["geography"] = "1245710558...1245710560"
    query_params["MEASURES"] = "20100"
    table = self.api.get_data(table, table_internal, query_params)
    self.assertEqual(table.shape, (21, 3))
    self.assertEqual(sum(table.OBS_VALUE), 8214)
    
  def test_get_and_add_descriptive_column(self):

    table_name = "KS401EW"
    # try to load locally first
    meta = self.api.load_metadata(table_name)

    query_params = {}
    query_params["CELL"] = "7...13"
    query_params["date"] = "latest"
    query_params["RURAL_URBAN"] = "0"
    query_params["select"] = "GEOGRAPHY_CODE,CELL,OBS_VALUE"
    query_params["geography"] = "1245710558...1245710560"
    query_params["MEASURES"] = "20100"
    table = self.api.get_data(table_name, meta["nomis_table"], query_params)
    self.assertEqual(table.shape, (21, 3))
    self.assertEqual(sum(table.OBS_VALUE), 8214)
    
    # first ensure table is unmodified if column doesnt exist
    old_cols = len(table.columns)
    self.api.convert_code(table, "NOT_THERE", meta)
    self.assertTrue(len(table.columns) == old_cols)
    
    self.api.convert_code(table, "CELL", meta)
    
    self.assertTrue(table.at[0,"CELL_NAME"] == "Whole house or bungalow: Detached")
    self.assertTrue(table.at[1,"CELL_NAME"] == "Whole house or bungalow: Semi-detached")
    self.assertTrue(table.at[2,"CELL_NAME"] == "Whole house or bungalow: Terraced (including end-terrace)")
    self.assertTrue(table.at[3,"CELL_NAME"] == "Flat, maisonette or apartment: Purpose-built block of flats or tenement")
    self.assertTrue(table.at[4,"CELL_NAME"] == "Flat, maisonette or apartment: Part of a converted or shared house (including bed-sits)")
    self.assertTrue(table.at[5,"CELL_NAME"] == "Flat, maisonette or apartment: In a commercial building")
    self.assertTrue(table.at[6,"CELL_NAME"] == "Caravan or other mobile or temporary structure")

  def test_get_geog_from_names(self):
    result = self.query.get_geog_from_names(["Leeds"], Api.Nomisweb.OA)
    self.assertEqual(result, '1254151943...1254154269,1254258198...1254258221,1254261711...1254261745,1254261853...1254261870,1254261894...1254261918,1254262125...1254262142,1254262341...1254262353,1254262394...1254262398,1254262498...1254262532,1254262620...1254262658,1254262922...1254262925')

    result = self.query.get_geog_from_names(["Newcastle upon Tyne"], Api.Nomisweb.LSOA)
    self.assertEqual(result, '1249910667...1249910832,1249935220...1249935228')

    result = self.query.get_geog_from_names(["Leeds", "Bradford"], Api.Nomisweb.MSOA)
    self.assertEqual(result, '1245710411...1245710471,1245710558...1245710660,1245714998...1245714998,1245715007...1245715007,1245715021...1245715022')

  def test_get_geog_from_codes(self):
    result = self.query.api.get_geo_codes([Api.Nomisweb.EnglandWales], Api.Nomisweb.LAD)
    self.assertEqual(result, '1946157057...1946157404')
    
  def test_geoquery(self):
    import inst.examples.geoquery as eg_geo
    eg_geo.main()

  # just checks code snippet runs ok (i.e. returns 0)
  def test_code_snippet(self):
    table = "KS401EW" 
    meta = self.api.get_metadata(table)
    query_params = {}
    query_params["CELL"] = "7...13"
    query_params["date"] = "latest"
    query_params["RURAL_URBAN"] = "0"
    query_params["select"] = "GEOGRAPHY_CODE,CELL,OBS_VALUE"
    query_params["geography"] = "1245710558...1245710560"
    query_params["MEASURES"] = "20100"

    self.query.write_code_snippets(table, meta, query_params)
    self.assertTrue(os.system("python3 " + self.api.cache_dir + table + ".py") == 0)
    # fails on travis because R isnt installed 
    #self.assertTrue(os.system("Rscript " + self.api.cache_dir + table + ".R") == 0)
