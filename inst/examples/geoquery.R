
library("UKCensusAPI")

cacheDir = "/tmp/UKCensusAPI"

# Here's a predefined query using Leeds at MSOA resolution,
# but we want to change the geographical area and refine the resolution
table = "KS401EW"
table_internal = "NM_618_1"
queryParams = list(
  date = "latest",
  RURAL_URBAN = "0",
  MEASURES = "20100",
  CELL = "7...13",
  geography = "1245710558...1245710660,1245714998...1245714998,1245715007...1245715007,1245715021...1245715022",
  select = "GEOGRAPHY_CODE,CELL,OBS_VALUE"
)

api = instance(cacheDir)

# Define the new region and resolution
coverage = c("City of London")
resolution = 299 # OA - see NomiswebApi.py

# Modify the query
coverageCodes = getLADCodes(api, coverage)
queryParams["geography"] = geoCodes(api, coverageCodes, resolution)

# Fetch the new data
KS401EW = getData(api, table, table_internal, queryParams)

