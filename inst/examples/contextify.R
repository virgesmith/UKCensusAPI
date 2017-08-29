
library("UKCensusAPI")

cacheDir = "/tmp/UKCensusAPI"

# Here's a predefined query, to which we add contextual data

table = "KS401EW"
table_internal = "NM_618_1"
queryParams = list(
  date = "latest",
  RURAL_URBAN = "0",
  MEASURES = "20100",
  CELL = "7...13",
  geography = "1245710558...1245710660",
  select = "GEOGRAPHY_CODE,CELL,OBS_VALUE"
)

api = instance(cacheDir)

# Fetch the data
KS401EW = getData(api, table, table_internal, queryParams)

# Add the context...
# TODO dataframes not compatible, need a function to return just the column lookup (as a dict?)
#contextify(api, table, "CELL", KS401EW)
head(KS401EW)
