from unittest import TestCase

import ukcensusapi.Nomisweb as Api
#import ukcensusapi.query as query

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

