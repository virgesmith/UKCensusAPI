# nomisweb.co.uk RESTful API interface

# TODO remove these
NomiswebApi.url <- "https://www.nomisweb.co.uk/"
NomiswebApi.key = Sys.getenv("NOMIS_API_KEY")

# TODO should these be removed?
library(digest)
library(rjson)
library(data.table)
library(reticulate)

#' get an instance of the python API (required to call any of the functions)
#'
#' @param cacheDir directory to cache data
#' @return an instance of the ukcensusweb api
#' @export
#' @examples
#'system("./setup.py install")
#' api = UKCensusAPI::instance("./")
instance = function(cacheDir) {
  # hack to ensure python module is installed
  # py_run_file("script.py") see https://cran.r-project.org/web/packages/reticulate/vignettes/introduction.html
  Api = reticulate::import("ukcensusapi.Nomisweb")
  api = Api$Nomisweb(cacheDir)
  return(api)
}


# Store your api key in .Renviron for access via Sys.getenv("NOMIS_API_KEY")

#' Interactive metadata query
#'
#' This function calls an interactive script where the user selects a table, a geography, and selects fields, optionally filtering by value.
#' This script will not run in RStudio due to the way it handles standard input. Please run in a standalone R session (or call the python script directly)
#' @export
#' @examples
#' queryMetadata()
queryMetadata = function() {
  # first check we are not running in RStudio (in which can we cannot run interatively, since RStudio redirects stdin from /dev/null)
  if (.Platform$GUI == "RStudio") {
    cat("This interactive code cannot be run from within RStudio due to the way RStudio handles stdin.\n")
    cat("Please either run it from a standalone R session, or call the python code (interactive.py) directly\n")
  } else {
    system("./interactive.py")
  }
}

#' getData()
#' Fetch and cache census data using a predefined query
#'
#' @export
#' @param queryUrl a predefined query
#' @param cacheDir directory to cache the tables in
#' @examples
#' queryUrl = "https://www.nomisweb.co.uk/api/v01/dataset/NM_618_1.data.tsv?CELL=7...13&MEASURES=20100&RURAL_URBAN=0&date=latest&geography=1245710558...1245710660%2C1245714998...1245714998%2C1245715007...1245715007%2C1245715021...1245715022&select=GEOGRAPHY_CODE%2CCELL%2COBS_VALUE"
#' getData(queryUrl, "./")
getData = function(queryUrl, cacheDir) {
  # append API key to query
  queryUrl = paste0(queryUrl, "&uid=", Sys.getenv("NOMIS_API_KEY"))

  # in typical R fashion, digest will do something nonstandard unless you override defaulted arguments
  filename <- paste0(cacheDir, digest(queryUrl, "md5", serialize=F), ".tsv")
  # used cached data if available, otherwise download. md5sum should ensure data file exactly matches query
  if (!file.exists(filename)) {
    curl::curl_download(queryUrl, filename)
  } else {
    print(paste("using cached data:", filename))
  }
  result <- read.csv(filename, sep="\t", stringsAsFactors = FALSE)
  return (result)
}


#' Map local authority names to nomisweb codes
#'
#' @param laNames a string vector of local authority names.
#' @return an integer vector of nomisweb local authority codes
#' @export
readLADCodes = function(laNames) {
  data(laMapping)
  codes = c()
  for (laName in laNames) {
    codes = append(codes, laMapping[laMapping$name == laName,]$nomiscode)
  }
  return(codes)
}

#' Map local authority names to nomisweb codes (python)
#'
#' @param api an instance of the UKCensusData API.
#' @param laNames a string vector of local authority names.
#' @return an integer vector of nomisweb local authority codes
#' @export
getLADCodes = function(api, laNames) {
  return(api$get_lad_codes(laNames))
}

#' geoCodes
#' Get nomisweb geographical codes for a region
#'
#' @param coverage an integer vector of nomisweb geographical codes
#' @param resolution the nomisweb code for a particular area type (e.g. 297 for MSOA)
#' @export
geoCodes = function(coverage, resolution) {

  if (NomiswebApi.key == "") {
    warning("Warning, no API key specified. Download will be limited to 25000 rows. Register at https://www.nomisweb.co.uk to get an API key and add NOMIS_API_KEY=<key> to your .Renviron")
  }
  # see https://www.nomisweb.co.uk/forum/posts.aspx?tID=555&fID=2

  geogCodes = c()
  for (c in coverage) {
    queryUrl = httr::modify_url(NomiswebApi.url, path = paste0("/api/v01/dataset/NM_144_1/geography/", c, "TYPE", resolution,".def.sdmx.json"))#, query = list))

    #print(queryUrl)

    result <- fromJSON(file=paste0(queryUrl))
    nResults = length(result$structure$codelists$codelist[[1]]$code)
    #print(paste(nResults, "results"))

    if (nResults > 0) {
      for (i in 1:length(result$structure$codelists$codelist[[1]]$code)) {
        geogCodes = append(geogCodes, result$structure$codelists$codelist[[1]]$code[[i]]$value)
      }
    }
  }
  return(shortenCodeList(geogCodes))
}

#' modifyGeography
#' Takes an existing nomisweb query and modifies the geography parameter according sipplied coverage and resolution
#'
#' @param queryUrl a predefined query url
#' @param coverage a
#' @param resolution the nomisweb code for a particular area type (e.g. 297 for MSOA)
#' @return a modified query
#' @examples
#' queryUrl = "https://www.nomisweb.co.uk/api/v01/dataset/NM_618_1.data.tsv?CELL=7...13&MEASURES=20100&RURAL_URBAN=0&date=latest&geography=1245710558...1245710660%2C1245714998...1245714998%2C1245715007...1245715007%2C1245715021...1245715022&select=GEOGRAPHY_CODE%2CCELL%2COBS_VALUE"
#' coverage = c("Leeds","Bradford")
#' resolution = 299
#' newQueryUrl = modifyGeography(queryUrl, coverage, resolution)
#' @export
modifyGeography = function(queryUrl, coverage, resolution) {

  coverageCodes = readLADCodes(coverage)

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

  return(newQueryUrl)
}

# not exported...
# this code orders and shinks the code lists (need to be aware of http header length restrictions)
shortenCodeList = function(codeList) {

  if (length(codeList) == 0)
    return("")
  if (length(codeList) == 1)
    return(as.character(codeList[1]))

  slist = sort(codeList)
  index1=1
  string = ""
  for (index2 in 2:length(slist)) {
    # check for a break
    if (slist[index2] != slist[index2-1] + 1)
    {
      if (index1 == index2) {
        string = paste0(string, as.character(slist[index1]), ",")
      }
      else {
        string = paste0(string, as.character(slist[index1]), "...", as.character(slist[index2-1]), ",")
      }
      index1 = index2
    }
  }
  if (index1 == index2) {
    string = paste0(string, as.character(slist[index1]))
  } else {
    string = paste0(string, as.character(slist[index1]), "...", as.character(slist[index2]))
  }
}
