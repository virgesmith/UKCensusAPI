
# See e.g. https://www.datamentor.io/r-programming/reference-class
# NRScotland class
#library(reticulate)

NRScotland <- setRefClass("NRScotland",
                          fields=c("api"),
                          methods=list(
                            test = function() { return(3) },
                            getMetadata = function(table, geog) {
                              return (api$get_metadata(table, geog))
                            }
                          ))

# can i (re)define new?
apiSC <- NRScotland$new(api = reticulate::import("ukcensusapi.NRScotland", delay_load = TRUE)$NRScotland("/tmp/UKCensusAPI"))

apiSC$getMetadata("KS401SC", "LAD")
