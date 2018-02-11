###############################################################
# Example: Annotating data from metadata
#
# shows how raw data can be annotated with meaningful metadata
###############################################################

library("UKCensusAPI")

cacheDir = "/tmp/UKCensusAPI"

# Here's a predefined query, to which we add contextual data

table = "KS401EW"
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
KS401EW = getData(api, table, queryParams)

# Add the context...
KS401EW = contextify(api, table, "CELL", KS401EW)
head(KS401EW)

# end of example

