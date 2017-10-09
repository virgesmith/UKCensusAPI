#' UKCensusAPI
#'
#' R package for automating queries and downloads of UK census data.
#'
#' Put your api key in .Renviron as "NOMIS_API_KEY"
#' See README.md for detailed information and examples.
#'
#' @section Functions:
#' \code{\link{geoCodeLookup}}
#'
#' \code{\link{geoCodes}}
#'
#' \code{\link{getData}}
#'
#' \code{\link{getLADCodes}}
#'
#' \code{\link{getMetadata}}
#'
#' \code{\link{instance}}
#'
#' \code{\link{queryInstance}}
#'
#' \code{\link{queryMetadata}}
#'
#' \code{\link{contextify}}
#'
#' @docType package
#' @name UKCensusAPI
NULL

Api <- NULL
Query <- NULL

.onLoad <- function(libname, pkgname) {
  Api <<- reticulate::import("ukcensusapi.Nomisweb", delay_load = TRUE)
  Query <<- reticulate::import("ukcensusapi.Query", delay_load = TRUE)
}

#' get an instance of the python API (required to call any of the functions)
#'
#' @param cacheDir directory to cache data
#' @return an instance of the ukcensusweb api
#' @export
instance = function(cacheDir) {
  # TODO can we have a function-static variable here?
  api = Api$Nomisweb(cacheDir)
  return(api)
}

#' get an instance of the python query (required to call any of the functions)
#'
#' @param api an instance of the ukcensusapi
#' @return an instance of the query module
#' @export
queryInstance = function(api) {
  # TODO can we have a function-static variable here?
  query = Query$Query(api)
  return(query)
}
