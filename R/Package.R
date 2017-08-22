
 Api <- NULL

.onLoad <- function(libname, pkgname) {
  Api <<- reticulate::import("ukcensusapi.Nomisweb", delay_load = TRUE)
}
