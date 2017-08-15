from unittest import TestCase

import ukcensusapi.Nomisweb as Api
import ukcensusapi.Query as Census

class Test(TestCase):
  api = Api.Nomisweb("/tmp")
  query = Census.Query(api)

  # just to ensure test harness works
  def test_init(self):
    self.assertTrue(True)

  def test_getLADCodes(self):
    self.assertTrue(self.api.getLADCodes("Royston Vasey") == [])
    self.assertTrue(self.api.getLADCodes("Leeds") == [1946157127])    
    self.assertTrue(self.api.getLADCodes(["Leeds","Bradford"]) == [1946157127, 1946157124])
    
  # This overlaps test_getGeographyFromCodes 
  def test_geoCodes(self):
    result = self.api.geoCodes([Api.Nomisweb.EnglandWales], Api.Nomisweb.LAD)
    self.assertTrue(result == '1946157057...1946157404')
    result = self.api.geoCodes([1946157127], Api.Nomisweb.OA)
    self.assertTrue(result ==  '1254151943...1254154269,1254258198...1254258221,1254261711...1254261745,1254261853...1254261870,1254261894...1254261918,1254262125...1254262142,1254262341...1254262353,1254262394...1254262398,1254262498...1254262532,1254262620...1254262658,1254262922...1254262925')

  def test_getUrl(self):
    self.assertTrue(True)

  def test_getData(self):
    self.assertTrue(True)

  def test_getMetadata(self):
    self.assertTrue(True)

  def test_getGeographyFromNames(self):
    result = self.query.getGeographyFromNames(["Leeds"], Api.Nomisweb.OA)
    self.assertTrue(result ==  '1254151943...1254154269,1254258198...1254258221,1254261711...1254261745,1254261853...1254261870,1254261894...1254261918,1254262125...1254262142,1254262341...1254262353,1254262394...1254262398,1254262498...1254262532,1254262620...1254262658,1254262922...1254262925')

    result = self.query.getGeographyFromNames(["Newcastle upon Tyne"], Api.Nomisweb.LSOA)
    self.assertTrue(result == '1249910667...1249910832,1249935220...1249935228')

    result = self.query.getGeographyFromNames(["Leeds","Bradford"], Api.Nomisweb.MSOA)
    self.assertTrue(result ==  '1245710411...1245710471,1245710558...1245710660,1245714998...1245714998,1245715007...1245715007,1245715021...1245715022')

  def test_getGeographyFromCodes(self):
    result = self.query.getGeographyFromCodes([Api.Nomisweb.EnglandWales], Api.Nomisweb.LAD)
    self.assertTrue(result == '1946157057...1946157404')
    

