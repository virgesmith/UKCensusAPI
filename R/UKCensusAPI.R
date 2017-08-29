#' UKCensusAPI
#'
#' R package for automating queries and downloads of UK census data.
#'
#' See README.md for detailed information and examples.
#'
#' @section Functions:
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
