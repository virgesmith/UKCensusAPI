import numpy as np

def test_geo_codes_sc(api_sc):
  lads = sorted(['S12000033', 'S12000034', 'S12000041', 'S12000035', 'S12000026', 'S12000005',
                  'S12000039', 'S12000006', 'S12000042', 'S12000008', 'S12000045', 'S12000010',
                  'S12000011', 'S12000036', 'S12000014', 'S12000015', 'S12000046', 'S12000017',
                  'S12000018', 'S12000019', 'S12000020', 'S12000021', 'S12000044', 'S12000023',
                  'S12000024', 'S12000038', 'S12000027', 'S12000028', 'S12000029', 'S12000030',
                  'S12000040', 'S12000013'])

  msoa_ab = sorted(['S02001275', 'S02001238', 'S02001237', 'S02001236', 'S02001278', 'S02001284',
                    'S02001247', 'S02001249', 'S02001246', 'S02001250', 'S02001261', 'S02001252',
                    'S02001251', 'S02001257', 'S02001258', 'S02001254', 'S02001256', 'S02001253',
                    'S02001248', 'S02001242', 'S02001240', 'S02001241', 'S02001239', 'S02001243',
                    'S02001259', 'S02001260', 'S02001264', 'S02001265', 'S02001268', 'S02001269',
                    'S02001267', 'S02001274', 'S02001266', 'S02001263', 'S02001262', 'S02001245',
                    'S02001270', 'S02001272', 'S02001273', 'S02001271', 'S02001244', 'S02001279',
                    'S02001282', 'S02001281', 'S02001280', 'S02001276', 'S02001277', 'S02001283',
                    'S02001255'])

  result = sorted(api_sc.get_geog("S92000003", "LAD"))
  assert np.array_equal(result, lads)
  result = sorted(api_sc.get_geog("S12000033", "MSOA11"))
  assert np.array_equal(result, msoa_ab)
  result = api_sc.get_geog("S12000033", "LSOA11")
  assert len(result) == 283
  result = api_sc.get_geog("S12000033", "OA11")
  assert len(result) == 1992


def test_get_metadata_sc(api_sc):
  # Scotland
  meta = api_sc.get_metadata("KS401SC", "LAD")
  assert meta["table"] == 'KS401SC'
  assert meta["geography"] == 'LAD'
  assert 'KS401SC_0_CODE' in meta["fields"]


def test_get_data_sc(api_sc):
  table_name = "KS401SC"
  geography = "S12000033" # Aberdeen
  categories = { "KS401SC_0_CODE": range(8,15) }
  table = api_sc.get_data(table_name, geography, "LAD", categories)
  assert table.shape == (7, 3)
  assert sum(table.OBS_VALUE) == 108153

  table_name = "DC2101SC"
  geography = "S12000033" # Aberdeen
  categories = { "DC2101SC_0_CODE": 4, # White Irish
                 "DC2101SC_1_CODE": [1, 2], # M+F
                 "DC2101SC_2_CODE": [6, 7, 8, 9, 10, 11, 12] } # 18-49
  table = api_sc.get_data(table_name, geography, "LAD", categories)
  assert table.shape == (14, 5)
  assert sum(table.OBS_VALUE) == 1732


