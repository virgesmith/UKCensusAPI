
import numpy as np


def test_geo_codes_ni(api_ni):
  # NI data
  lads = ['95AA', '95BB', '95CC', '95DD', '95EE', '95FF', '95GG', '95HH', '95II', '95JJ', '95KK', '95LL', '95MM',
          '95NN', '95OO', '95PP', '95QQ', '95RR', '95SS', '95TT', '95UU', '95VV', '95WW', '95XX', '95YY', '95ZZ']

  msoa_95aa = ['95AA01', '95AA02', '95AA03', '95AA04', '95AA05', '95AA06', '95AA07', '95AA08', '95AA09', '95AA10', '95AA11', '95AA12',
                '95AA13', '95AA14', '95AA15', '95AA16', '95AA17', '95AA18', '95AA19']
  lsoa_95aa = ['95AA01S1', '95AA01S2', '95AA01S3', '95AA02W1', '95AA03W1', '95AA04W1', '95AA05W1', '95AA06S1', '95AA06S2', '95AA07W1', '95AA08W1',
                '95AA09W1', '95AA10W1', '95AA11S1', '95AA11S2', '95AA12W1', '95AA13S1', '95AA13S2', '95AA14W1', '95AA15S1', '95AA15S2', '95AA16W1',
                '95AA17W1', '95AA18W1', '95AA19W1']

  result = sorted(api_ni.get_geog("N92000002", "LAD"))
  assert np.array_equal(result, lads)
  result = sorted(api_ni.get_geog("95AA", "MSOA11"))
  assert np.array_equal(result, msoa_95aa)
  result = sorted(api_ni.get_geog("95AA", "LSOA11"))
  assert np.array_equal(result, lsoa_95aa)
  result = sorted(api_ni.get_geog("95AA", "OA11"))
  assert len(result) == 129


def test_get_metadata_ni(api_ni):
  # NI
  meta = api_ni.get_metadata("QS401NI", "LSOA11")
  assert meta["table"] == 'QS401NI'
  assert meta["geography"] == 'SOA'
  assert 'QS401NI_0_CODE' in meta["fields"]
  assert len(meta["fields"]['QS401NI_0_CODE']) == 12


def test_get_data_ni(api_ni):
  table_name = "QS401NI"
  geography = "95AA" # Antrim
  categories = { "QS401NI_0_CODE": [1,6,8,9,10] }
  table = api_ni.get_data(table_name, geography, "LAD", categories)
  assert table.shape == (5, 3)
  assert sum(table.OBS_VALUE) == 52454

  table_name = "QS202NI"
  geography = "95ZZ" # Strabane
  categories = { "QS202NI_0_CODE": [1,2,3,4,5,6] }
  table = api_ni.get_data(table_name, geography, "MSOA11", categories)
  assert table.shape == (96, 3)
  assert sum(table.OBS_VALUE) == 14817

