
# Disable "Invalid constant name", "Line too long"
# pylint: disable=C0103,C0301

from unittest import TestCase

import ukcensusapi.Nomisweb as Api
import ukcensusapi.Query as Census

# test methods only run if prefixed with "test"
class Test(TestCase):
  api = Api.Nomisweb("/tmp")
  query = Census.Query(api)

  def test_get_lad_codes(self):
    self.assertTrue(self.api.get_lad_codes("Royston Vasey") == [])
    self.assertTrue(self.api.get_lad_codes("Leeds") == [1946157127])
    self.assertTrue(self.api.get_lad_codes(["Leeds", "Bradford"]) == [1946157127, 1946157124])

  # This overlaps test_getGeographyFromCodes
  def test_geo_codes(self):
    result = self.api.get_geo_codes([Api.Nomisweb.EnglandWales], Api.Nomisweb.LAD)
    self.assertTrue(result == '1946157057...1946157404')
    result = self.api.get_geo_codes([1946157127], Api.Nomisweb.OA)
    self.assertTrue(result == '1254151943...1254154269,1254258198...1254258221,1254261711...1254261745,1254261853...1254261870,1254261894...1254261918,1254262125...1254262142,1254262341...1254262353,1254262394...1254262398,1254262498...1254262532,1254262620...1254262658,1254262922...1254262925')

#  # TODO
#  def test_get_url(self):
#    self.assertTrue(True)

#  # TODO
#  def test_get_data(self):
#    self.assertTrue(True)

#  # TODO
#  def test_get_metadata(self):
#    self.assertTrue(True)

  def test_get_geog_from_names(self):
    result = self.query.get_geog_from_names(["Leeds"], Api.Nomisweb.OA)
    self.assertTrue(result == '1254151943...1254154269,1254258198...1254258221,1254261711...1254261745,1254261853...1254261870,1254261894...1254261918,1254262125...1254262142,1254262341...1254262353,1254262394...1254262398,1254262498...1254262532,1254262620...1254262658,1254262922...1254262925')

    result = self.query.get_geog_from_names(["Newcastle upon Tyne"], Api.Nomisweb.LSOA)
    self.assertTrue(result == '1249910667...1249910832,1249935220...1249935228')

    result = self.query.get_geog_from_names(["Leeds", "Bradford"], Api.Nomisweb.MSOA)
    self.assertTrue(result == '1245710411...1245710471,1245710558...1245710660,1245714998...1245714998,1245715007...1245715007,1245715021...1245715022')

  def test_get_geog_from_codes(self):
    result = self.query.get_geog_from_codes([Api.Nomisweb.EnglandWales], Api.Nomisweb.LAD)
    self.assertTrue(result == '1946157057...1946157404')
