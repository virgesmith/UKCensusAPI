
#' Interactive metadata query
#'
#' This function calls an interactive script where the user selects a table, a geography, and selects fields, optionally filtering by value.
#' This script will not run in RStudio due to the way it handles standard input. Please run in a standalone R session (or call the python script directly)
#' @export
queryMetadata = function() {
  # first check we are not running in RStudio (in which can we cannot run interatively, since RStudio redirects stdin from /dev/null)
  if (.Platform$GUI == "RStudio") {
    cat("This interactive code cannot be run from within RStudio due to the way RStudio handles stdin.\n")
    cat("Please either run it from a standalone R session, or call the python code (interactive.py) directly\n")
  } else {
    system("scripts/interactive.py")
  }
}

#' getMetadata()
#' Fetch the metadata for a census table
#'
#' @export
#' @param api the census provider api
#' @param tableName the name of the census table
getMetadata = function(api, tableName) {
  return(api$get_metadata(tableName))
}

#' getData()
#' Fetch and cache census data using a predefined query
#'
#' Ensure all query numeric parameters are passed as strings (e.g. "0" not 0)
#' This prevents conversion to floating-point which can makie queries fail
#' @param api a predefined query
#' @param tableName name of census table (e.g KS401EW)
#' @param internalName internal name of census table (e.g NM_618_1)
#' @param query query parameters
#' @export
getData = function(api, tableName, internalName, query) {
  # returned value is filename (or error) to avoid data frame compatibility issues
  filename = api$get_data(tableName, internalName, query, TRUE)
  # TODO check that string isnt an error!
  return(read.csv(filename, sep="\t", stringsAsFactors = FALSE))
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
#' @param api the instance of the an integer vector of nomisweb geographical codes
#' @param coverage an integer vector of nomisweb geographical codes
#' @param resolution the nomisweb code for a particular area type (e.g. 297 for MSOA)
#' @export
geoCodes = function(api, coverage, resolution) {
  # force correct types
  return(api$get_geo_codes(as.integer(coverage), as.integer(resolution)))
}

#' contextify
#'
#' Append table with a contextual column.
#'
#' @param api the instance of the an integer vector of nomisweb geographical codes
#' @param tableName name of census table
#' @param columnName name of column in the table
#' @param table the table
#' @return no return value, table is modified in-place
#' @export
contextify = function(api, tableName, columnName, table) {
  metadata = api$load_metadata(tableName)
  # append a column using the value lookup provided by the metadata...
  # Look at R go! such exquisitely beautiful and intuitive syntax
  table[paste0(columnName, "_NAME")] = unlist(metadata$fields[columnName][[1]][as.character(table[[columnName]])])
  return(table)
}
