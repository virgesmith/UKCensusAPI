
Api <- NULL
Query <- NULL

.onLoad <- function(libname, pkgname) {
  Api <<- reticulate::import("ukcensusapi.Nomisweb", delay_load = TRUE)
  Query <<- reticulate::import("ukcensusapi.Query", delay_load = TRUE)
}
