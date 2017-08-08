# nomisweb.co.uk RESTful API interface

# AVOID ADDING GLOBAL VARIABLE DEFINITIONS IN THIS FILE
# THEY SHOULD BE DEFINED IN THE CALLING SCRIPT
# IF ABSOLUTELY NECESSARY, PREFIX THE VARIABLE NAME WITH THE NAME OF THIS SOURCE FILE
NomiswebApi.url <- "https://www.nomisweb.co.uk/"
NomiswebApi.key = Sys.getenv("NOMIS_API_KEY")


library(digest)
library(rjson)
library(data.table)

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

#' Fetch census data
#'
#' This function ...
#' @export
#' @examples
#' queryMetadata()
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
#' This function ...
#' @export
readLADCodes = function(laNames) {
  data(laMapping)
  codes = c()
  for (laName in laNames) {
    codes = append(codes, laMapping[laMapping$name == laName,]$nomiscode)
  }
  return(codes)
}

#' Get nomisweb geographical codes for a region
#'
#' This function ...
#' @export
geoCodes = function(coverage, resolution) {

  if (NomiswebApi.key == "") {
    warning("Warning, no API key specified. Download will be limited to 25000 rows. Register at https://www.nomisweb.co.uk to get an API key and add NOMIS_API_KEY=<key> to your .Renviron")
  }
  # see https://www.nomisweb.co.uk/forum/posts.aspx?tID=555&fID=2

  geogCodes = c()
  for (c in coverage) {
    queryUrl = httr::modify_url(NomiswebApi.url, path = paste0("/api/v01/dataset/NM_144_1/geography/", c, "TYPE", resolution,".def.sdmx.json"))#, query = list))

    print(queryUrl)

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


# not exported...
# this code orders and shinks the code lists (need to be aware of http header length restrictions)
shortenCodeList = function(codeList) {
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
