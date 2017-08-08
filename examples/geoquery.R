
# this example code is an interim solution pending proper R-python integration
#source("../R/src/NomiswebApi.R")

cacheDir = "../data/"
queryUrl = "https://www.nomisweb.co.uk/api/v01/dataset/NM_618_1.data.tsv?CELL=7...13&MEASURES=20100&RURAL_URBAN=0&date=latest&geography=1245710558...1245710660%2C1245714998...1245714998%2C1245715007...1245715007%2C1245715021...1245715022&select=GEOGRAPHY_CODE%2CCELL%2COBS_VALUE"

coverage = c("Leeds","Bradford")
# Define the new resolution
resolution = 299 # OA - see NomiswebApi.py
# Convert the coverage area into nomis codes
coverageCodes = readLADCodes(coverage, "../persistent_data/laMapping.csv")

newGeography = geoCodes(coverageCodes, resolution)

# Hack the url (pending a better (python) solution)
# , -> %2C for url encoding
newGeography = gsub(",", "%2C", newGeography)
# reassemble the query URL
# get the position geography param starts
gpos = regexpr("geography=", queryUrl) + 9
# get the part of the query after the geography param
remQuery = substring(substring(queryUrl, gpos), regexpr("\\&", substring(queryUrl, gpos)))

newQueryUrl = paste0(substring(queryUrl, 1, gpos), newGeography, remQuery)

KS401EW = NomiswebApi.getData(newQueryUrl, cacheDir)

