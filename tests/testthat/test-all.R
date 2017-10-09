#  see http://kbroman.org/pkg_primer/pages/tests.html

context("UKCensusAPI")
library(reticulate)

api = UKCensusAPI::instance("/tmp/UKCensusAPI")

# TODO not sure we need this now (since above works)
# helper function to skip tests if we don't have the python module
skip_if_no_python_api = function() {
  if (!py_module_available("ukcensusapi.Nomisweb"))
    skip("python module ukcensusapi.Nomisweb not available, skipping test")
}

# simply checks we can get nomis geo codes back
test_that("geoCodeLookup", {
  expect_true(UKCensusAPI::geoCodeLookup(api, "MSOA11") == 297)
  expect_true(UKCensusAPI::geoCodeLookup(api, "LSOA01") == 304)
  expect_true(UKCensusAPI::geoCodeLookup(api, "LAD") == 464)
  expect_true(UKCensusAPI::geoCodeLookup(api, "EnglandWales") == 2092957703)
})

# simply checks we get data back
test_that("getMetadata", {
  skip_if_no_python_api()
  table = "KS401EW"
  expect_true(class(UKCensusAPI::getMetadata(api, table)) == "list")
})

# simply checks we get a data frame back
test_that("getData", {
  skip_if_no_python_api()
  table = "KS401EW"
  table_internal = "NM_618_1"
  query = list(date = "latest",
               geography = "1245714681...1245714688",
               CELL = "7...13",
               RURAL_URBAN="0",
               measures = "20100",
               select = "GEOGRAPHY_CODE,CELL,OBS_VALUE")
  expect_true(class(UKCensusAPI::getData(api, table, table_internal, query)) == "data.frame")

})

test_that("getLADCodes", {
  skip_if_no_python_api()
  expect_true(length(getLADCodes(api, c())) == 0)
  expect_true(length(getLADCodes(api, c("Framley"))) == 0)
  expect_true(getLADCodes(api, c("Leeds")) == 1946157127)
  expect_true(getLADCodes(api, c("Leeds")) == c(1946157127))

  codes = getLADCodes(api, c("Leeds", "Bradford", "Kirklees", "Wakefield", "Calderdale"))
  # == returns a bool vector, so check that its sum is its length
  expect_true(sum(codes == c(1946157127, 1946157124, 1946157126, 1946157128, 1946157125)) == length(codes))

  codes = getLADCodes(api, c("Leeds", "Bradford", "Skipdale", "Wakefield", "Calderdale"))
  # == returns a bool vector, so check that its sum is its length
  expect_true(sum(codes == c(1946157127, 1946157124, 1946157128, 1946157125)) == length(codes))

  codes = getLADCodes(api, c("Trumpton", "Camberwick Green", "Chigley"))
  # == returns a bool vector, so check that its sum is its length
  expect_true(length(codes) == 0)
})


test_that("geoCodes empty", {
  skip_if_no_python_api()
  expect_true(geoCodes(api, c(), 999) == "")
})

test_that("geoCodes invalid", {
  skip_if_no_python_api()
  expect_true(geoCodes(api, c(999), 999) == "")
})

test_that("geoCodes single LA", {
  skip_if_no_python_api()
  expect_true(geoCodes(api, 1946157124, 464) == "1946157124")
})

test_that("geoCodes multi MSOA", {
  skip_if_no_python_api()
  expect_true(geoCodes(api, c(1946157124, 1946157128), 297) == "1245710411...1245710471,1245710661...1245710705")
})

test_that("geoCodes multi LSOA", {
  skip_if_no_python_api()
  expect_true(geoCodes(api, c(1946157124, 1946157128), 298) == "1249912854...1249913154,1249913980...1249914188,1249935357...1249935365")
})

test_that("geoCodes single OA", {
  skip_if_no_python_api()
  expect_true(geoCodes(api, 1946157124, 299) == "1254148629...1254150034,1254267588...1254267709")
})

test_that("contextify", {
  skip_if_no_python_api()
  table = "KS401EW"
  table_internal = "NM_618_1"
  query = list(date = "latest",
               geography = "1245714681...1245714688",
               CELL = "7...13",
               RURAL_URBAN="0",
               measures = "20100",
               select = "GEOGRAPHY_CODE,CELL,OBS_VALUE")
  data = UKCensusAPI::getData(api, table, table_internal, query)
  column = "CELL"

  data = contextify(api, table, column, data)
  # check table has column
  expect_true("CELL_NAME" %in% colnames(data))
  # then check values
  expect_true(data$CELL_NAME[[1]] == "Whole house or bungalow: Detached")
  expect_true(data$CELL_NAME[[2]] == "Whole house or bungalow: Semi-detached")
  expect_true(data$CELL_NAME[[3]] == "Whole house or bungalow: Terraced (including end-terrace)")
  expect_true(data$CELL_NAME[[4]] == "Flat, maisonette or apartment: Purpose-built block of flats or tenement")
  expect_true(data$CELL_NAME[[5]] == "Flat, maisonette or apartment: Part of a converted or shared house (including bed-sits)")
  expect_true(data$CELL_NAME[[6]] == "Flat, maisonette or apartment: In a commercial building")
  expect_true(data$CELL_NAME[[7]] == "Caravan or other mobile or temporary structure")
})

test_that("geoquery example", {
  skip_if_no_python_api()
  # hack to get test to run as part of checks
  if (dir.exists("../../inst/examples")) {
    path = "../../inst/examples/"
  } else {
    path = "../../UKCensusAPI/examples/"
  }
  # # better to use system and Rscript?
  # ret = source(paste0(path, "geoquery.R"))
  # expect_true(class(ret) == "list")
  # run the R snippet in a separate process
  script = paste0("Rscript ", path, "geoquery.R")
  ret = system(script)
  expect_true(ret == 0)
})

test_that("contextify example", {
  skip_if_no_python_api()
  # hack to get test to run as part of checks
  if (dir.exists("../../inst/examples")) {
    path = "../../inst/examples/"
  } else {
    path = "../../UKCensusAPI/examples/"
  }
  # # better to use system and Rscript?
  # ret = source(paste0(path, "geoquery.R"))
  # expect_true(class(ret) == "list")
  # run the R snippet in a separate process
  script = paste0("Rscript ", path, "contextify.R")
  ret = system(script)
  expect_true(ret == 0)
})

test_that("code snippet", {
  skip_if_no_python_api()

  # generate a code snippet
  table = "KS401EW"
  meta = getMetadata(api, table)
  queryParams = list(
    CELL = "7...13",
    geography = "1245710558...1245710560",
    select = "GEOGRAPHY_CODE,CELL,OBS_VALUE",
    date = "latest",
    RURAL_URBAN = "0",
    MEASURES = "20100"
  )
  query = UKCensusAPI::queryInstance(api)
  query$write_code_snippets(table, meta, queryParams)

  # run the R snippet in a separate process
  script = paste0("Rscript ", api$cache_dir, table, ".R")
  ret = system(script)
  expect_true(ret == 0)
})
