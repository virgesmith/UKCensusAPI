
 Api <- NULL

.onLoad <- function(libname, pkgname) {
  # if (reticulate::py_available(initialize = TRUE)) {
  #   if (!reticulate::py_module_available("ukcensusapi.Nomisweb")) {
  #     print(getwd())
  #     print("ukcensusapi.Nomisweb not available, attempting to install")
  #     system("./setup.py install")
  #   }
  #   # if (!reticulate::py_module_available("ukcensusapi.Nomisweb")) {
  #   #   print(getwd())
  #   #   print("ukcensusapi.Nomisweb still not available")
  #   #   system("./setup.py install")
  #   # } else {
      Api <<- reticulate::import("ukcensusapi.Nomisweb", delay_load = TRUE)
      #}
  #}
}
