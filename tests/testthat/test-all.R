#  see http://kbroman.org/pkg_primer/pages/tests.html

context("UKCensusAPI")
library(reticulate)

apiEW = UKCensusAPI::instance("/tmp/UKCensusAPI")
apiSC = UKCensusAPI::instance("/tmp/UKCensusAPI", "SC")
apiNI = UKCensusAPI::instance("/tmp/UKCensusAPI", "NI")

# simply checks we can get nomis geo codes back
test_that("geoCodeLookup", {
  expect_true(UKCensusAPI::geoCodeLookup(apiEW, "MSOA11") == "TYPE297")
  expect_true(UKCensusAPI::geoCodeLookup(apiEW, "LSOA01") == "TYPE304")
  expect_true(UKCensusAPI::geoCodeLookup(apiEW, "LAD") == "TYPE464")
  expect_true(UKCensusAPI::geoCodeLookup(apiEW, "EnglandWales") == "2092957703")
})

# simply checks we get data back# simply checks we get data back
test_that("getMetadata", {
  table = "KS401EW"
  expect_true(class(UKCensusAPI::getMetadata(apiEW, table)) == "list")
})

# simply checks we get data back
test_that("getMetadataSC", {
  table = "KS401SC"
  expect_true(class(apiSC$getMetadata(table, "LAD")) == "list")
})

test_that("getMetadataNI", {
  table = "KS401NI"
  expect_true(class(apiNI$getMetadata(table, "LAD")) == "list")
})

# simply checks we get a data frame back
test_that("getData", {
  table = "KS401EW"
  query = list(date = "latest",
               geography = "1245714681...1245714688",
               CELL = "7...13",
               RURAL_URBAN="0",
               measures = "20100",
               select = "GEOGRAPHY_CODE,CELL,OBS_VALUE")
  expect_true(class(UKCensusAPI::getData(apiEW, table, query)) == "data.frame")
})

# simply checks we get a data frame back
test_that("getDataSC", {
  table = "KS401SC"
  region = "S12000033"
  resolution = "LAD"
  filter = list("KS401SC_0_CODE" = c(0,1,2,3))
  expect_true(class(apiSC$getData(table, region, resolution, filter)) == "data.frame")
})

# simply checks we get a data frame back
test_that("getDataNI", {
  table = "KS401NI"
  region = "95AA"
  resolution = "LAD"
  filter = list("KS401NI_0_CODE" = c(0,1,2,3))
  expect_true(class(apiNI$getData(table, region, resolution, filter)) == "data.frame")
})

# simply checks we get a data frame back
test_that("getOdData", {
  table = "WF01BEW"
  query = list(date = "latest",
               # OD are 5 LSOAs in central Leeds
               currently_residing_in = "1249934756...1249934758,1249934760,1249934761",
               place_of_work = "1249934756...1249934758,1249934760,1249934761",
               measures = "20100",
               select = "currently_residing_in_code,place_of_work_code,OBS_VALUE")
  expect_true(class(UKCensusAPI::getData(apiEW, table, query)) == "data.frame")
})

test_that("getLADCodes", {
  expect_true(length(getLADCodes(apiEW, c())) == 0)
  expect_true(length(getLADCodes(apiEW, c("Framley"))) == 0)
  expect_true(getLADCodes(apiEW, c("Leeds")) == 1946157127)
  expect_true(getLADCodes(apiEW, c("Leeds")) == c(1946157127))

  codes = getLADCodes(apiEW, c("Leeds", "Bradford", "Kirklees", "Wakefield", "Calderdale"))
  # == returns a bool vector, so check that its sum is its length
  expect_true(sum(codes == c(1946157127, 1946157124, 1946157126, 1946157128, 1946157125)) == length(codes))

  codes = getLADCodes(apiEW, c("Leeds", "Bradford", "Skipdale", "Wakefield", "Calderdale"))
  # == returns a bool vector, so check that its sum is its length
  expect_true(sum(codes == c(1946157127, 1946157124, 1946157128, 1946157125)) == length(codes))

  codes = getLADCodes(apiEW, c("Trumpton", "Camberwick Green", "Chigley"))
  # == returns a bool vector, so check that its sum is its length
  expect_true(length(codes) == 0)
})

test_that("geoCodes empty", {
  expect_true(geoCodes(apiEW, c(), "TYPE999") == "")
})

test_that("geoCodes invalid", {
  expect_true(geoCodes(apiEW, c(999), "TYPE999") == "")
})

test_that("geoCodes single LA", {
  expect_true(geoCodes(apiEW, 1946157124, "TYPE464") == "1946157124")
})

test_that("geoCodes multi MSOA", {
  expect_true(geoCodes(apiEW, c(1946157124, 1946157128), "TYPE297") == "1245710411...1245710471,1245710661...1245710705")
})

test_that("geoCodes multi LSOA", {
  expect_true(geoCodes(apiEW, c(1946157124, 1946157128), "TYPE298") == "1249912854...1249913154,1249913980...1249914188,1249935357...1249935365")
})

test_that("geoCodes single OA", {
  expect_true(geoCodes(apiEW, 1946157124, "TYPE299") == "1254148629...1254150034,1254267588...1254267709")
})

test_that("geoCodes SC", {
  expect_true(length(apiSC$getGeog("S12000033", "MSOA11")) == 49)
  expect_true(length(apiSC$getGeog("S12000033", "LSOA11")) == 283)
  expect_true(length(apiSC$getGeog("S12000033", "OA11")) == 1992)
})

test_that("geoCodes NI", {
  expect_true(length(apiNI$getGeog("95AA", "LAD")) == 1)
  expect_true(length(apiNI$getGeog("95AA", "MSOA11")) == 19)
  expect_true(length(apiNI$getGeog("95AA", "LSOA11")) == 25)
  expect_true(length(apiNI$getGeog("95AA", "OA11")) == 129)
})

test_that("contextify", {
  table = "KS401EW"
  query = list(date = "latest",
               geography = "1245714681...1245714688",
               CELL = "7...13",
               RURAL_URBAN="0",
               measures = "20100",
               select = "GEOGRAPHY_CODE,CELL,OBS_VALUE")
  data = UKCensusAPI::getData(apiEW, table, query)
  column = "CELL"

  data = contextify(apiEW, table, column, data)
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
  script = paste0(R.home("bin"), "/Rscript ", path, "geoquery.R")
  ret = system(script)
  expect_true(ret == 0)
})

test_that("contextify example", {
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
  script = paste0(R.home("bin"), "/Rscript ", path, "contextify.R")
  ret = system(script)
  expect_true(ret == 0)
})

test_that("code snippet", {

  # generate a code snippet
  table = "KS401EW"
  meta = getMetadata(apiEW, table)
  queryParams = list(
    CELL = "7...13",
    geography = "1245710558...1245710560",
    select = "GEOGRAPHY_CODE,CELL,OBS_VALUE",
    date = "latest",
    RURAL_URBAN = "0",
    MEASURES = "20100"
  )
  query = UKCensusAPI::queryInstance(apiEW$cache_dir)
  query$write_code_snippets(table, meta, queryParams)

  # run the R snippet in a separate process
  script = paste0(R.home("bin"), "/Rscript ", apiEW$cache_dir, "/", table, ".R")
  ret = system(script)
  expect_true(ret == 0)
})
