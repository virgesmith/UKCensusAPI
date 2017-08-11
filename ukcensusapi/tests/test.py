from unittest import TestCase

import ukcensusapi.Nomisweb as Api
import ukcensusapi.Query as Census

class Test(TestCase):

  # just to ensure test harness works
  def test_init(self):
    api = Api.Nomisweb("/tmp")
    self.assertTrue(True)

  def test_readLADCodes(self):
    api = Api.Nomisweb("/tmp")
    self.assertTrue(api.readLADCodes(["Leeds"]) == [1946157127])    
    self.assertTrue(api.readLADCodes(["Leeds","Bradford"]) == [1946157127, 1946157124])
    #self.assertTrue(api.readLADCodes(["Royston Vasey"]) == [])
    
  # TODO
  def test_geoCodes(self):
    self.assertTrue(True)

  def test_getUrl(self):
    self.assertTrue(True)

  def test_getData(self):
    self.assertTrue(True)

  def test_getMetadata(self):
    self.assertTrue(True)

  def test_getGeodata(self):
    self.assertTrue(True)

  def test_getGeographyFromNames(self):
    query = Census.Query.getGeographyFromNames(["Leeds"], Api.Nomisweb.OA)
    self.assertTrue(query ==  '1254151943...1254154269,1254258198...1254258221,1254261711...1254261745,1254261853...1254261870,1254261894...1254261918,1254262125...1254262142,1254262341...1254262353,1254262394...1254262398,1254262498...1254262532,1254262620...1254262658,1254262922...1254262925')

    query = Census.Query.getGeographyFromNames(["Newcastle upon Tyne"], Api.Nomisweb.LSOA)
    self.assertTrue(query == '1249910667...1249910832,1249935220...1249935228')

    query = Census.Query.getGeographyFromNames(["Leeds","Bradford"], Api.Nomisweb.MSOA)
    self.assertTrue(query ==  '1245710411...1245710471,1245710558...1245710660,1245714998...1245714998,1245715007...1245715007,1245715021...1245715022')

  def test_getGeographyFromCodes(self):
    query = Census.Query.getGeographyFromCodes([Api.Nomisweb.EnglandWales], Api.Nomisweb.LAD)
    self.assertTrue(query == '1228931073...1228931420')
    

