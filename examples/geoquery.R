
# this example code is an interim solution pending proper R-python integration
library("UKCensusAPI")

cacheDir = "./"
queryUrl = "https://www.nomisweb.co.uk/api/v01/dataset/NM_618_1.data.tsv?CELL=7...13&MEASURES=20100&RURAL_URBAN=0&date=latest&geography=1245710558...1245710660%2C1245714998...1245714998%2C1245715007...1245715007%2C1245715021...1245715022&select=GEOGRAPHY_CODE%2CCELL%2COBS_VALUE"

# Define the new region and resolution
coverage = c("Leeds","Bradford")
resolution = 299 # OA - see NomiswebApi.py

# Modify the url
newQueryUrl = modifyGeography(queryUrl, coverage, resolution)

# Fetch the new data
KS401EW = getData(newQueryUrl, cacheDir)

