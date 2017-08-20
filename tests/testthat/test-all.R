#  see http://kbroman.org/pkg_primer/pages/tests.html

context("UKCensusAPI")
library(reticulate)

# Regression tests

test_that("getData invalid cache", {
  cacheDir = "/"
  queryUrl = "https://www.nomisweb.co.uk/api/v01/dataset/NM_618_1.data.tsv?CELL=7...13&MEASURES=20100&RURAL_URBAN=0&date=latest&geography=1245710558...1245710660%2C1245714998...1245714998%2C1245715007...1245715007%2C1245715021...1245715022&select=GEOGRAPHY_CODE%2CCELL%2COBS_VALUE"
  expect_error(UKCensusAPI::getData(queryUrl, cacheDir))
})

# simple checks we get a data frame back
test_that("getData valid cache", {
  cacheDir = "./"
  queryUrl = "https://www.nomisweb.co.uk/api/v01/dataset/NM_618_1.data.tsv?CELL=7...13&MEASURES=20100&RURAL_URBAN=0&date=latest&geography=1245710558...1245710660%2C1245714998...1245714998%2C1245715007...1245715007%2C1245715021...1245715022&select=GEOGRAPHY_CODE%2CCELL%2COBS_VALUE"
  expect_true(class(UKCensusAPI::getData(queryUrl, cacheDir)) == "data.frame")
})

test_that("readLADCodes empty", {
  expect_true(length(readLADCodes(c())) == 0)
})

test_that("readLADCodes invalid", {
  expect_true(length(readLADCodes(c("Framley"))) == 0)
})

test_that("readLADCodes single", {
  expect_true(readLADCodes(c("Leeds")) == 1946157127)
  expect_true(readLADCodes(c("Leeds")) == c(1946157127))
})

test_that("readLADCodes multi", {
  codes = readLADCodes(c("Leeds", "Bradford", "Kirklees", "Wakefield", "Calderdale"))
  # == returns a bool vector, so check that its sum is its length
  expect_true(sum(codes == c(1946157127, 1946157124, 1946157126, 1946157128, 1946157125)) == length(codes))
})

test_that("readLADCodes multi with invalid", {
  codes = readLADCodes(c("Leeds", "Bradford", "Skipdale", "Wakefield", "Calderdale"))
  # == returns a bool vector, so check that its sum is its length
  expect_true(sum(codes == c(1946157127, 1946157124, 1946157128, 1946157125)) == length(codes))
})

test_that("readLADCodes multi all invalid", {
  codes = readLADCodes(c("Trumpton", "Camberwick Green", "Chigley"))
  # == returns a bool vector, so check that its sum is its length
  expect_true(length(codes) == 0)
})

test_that("getLADCodes python", {
  api = UKCensusAPI::instance("./")
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
  expect_true(geoCodes(c(), 999) == "")
})

test_that("geoCodes invalid", {
  expect_true(geoCodes(c(999), 999) == "")
})

test_that("geoCodes single LA", {
  expect_true(geoCodes(1946157124, 464) == "1946157124")
})

test_that("geoCodes multi MSOA", {
  expect_true(geoCodes(c(1946157124, 1946157128), 297) == "1245710411...1245710471,1245710661...1245710705")
})

test_that("geoCodes multi LSOA", {
  expect_true(geoCodes(c(1946157124, 1946157128), 298) == "1249912854...1249913154,1249913980...1249914188,1249935357...1249935365")
})

test_that("geoCodes single OA", {
  expect_true(geoCodes(1946157124, 299) == "1254148629...1254150034,1254267588...1254267709")
})

test_that("change coverage", {
  queryUrl = "https://www.nomisweb.co.uk/api/v01/dataset/NM_618_1.data.tsv?CELL=7...13&MEASURES=20100&RURAL_URBAN=0&date=latest&geography=1245710558...1245710660%2C1245714998...1245714998%2C1245715007...1245715007%2C1245715021...1245715022&select=GEOGRAPHY_CODE%2CCELL%2COBS_VALUE"
  newQueryUrl = modifyGeography(queryUrl, c("Newcastle upon Tyne"), 298)
  expect_true(newQueryUrl == "https://www.nomisweb.co.uk/api/v01/dataset/NM_618_1.data.tsv?CELL=7...13&MEASURES=20100&RURAL_URBAN=0&date=latest&geography=1249910667...1249910832%2C1249935220...1249935228&select=GEOGRAPHY_CODE%2CCELL%2COBS_VALUE")
})

