# Hack to make snippet test work in R CMD CHECK
# see https://github.com/hadley/testthat/issues/86
Sys.setenv("R_TESTS" = "")

library(testthat)
library(UKCensusAPI)
test_check("UKCensusAPI")
