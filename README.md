# UK Census Data API

[![PyPI version](https://badge.fury.io/py/ukcensusapi.svg)](https://badge.fury.io/py/ukcensusapi) [![Anaconda-Server Badge](https://anaconda.org/conda-forge/ukcensusapi/badges/version.svg)](https://anaconda.org/conda-forge/ukcensusapi) [![Anaconda-Server Badge](https://anaconda.org/conda-forge/ukcensusapi/badges/downloads.svg)](https://anaconda.org/conda-forge/ukcensusapi)

[![License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://opensource.org/licenses/MIT)[![JOSS status](http://joss.theoj.org/papers/40041a0ebb1364286d5eb144d333bb6a/status.svg)](http://joss.theoj.org/papers/40041a0ebb1364286d5eb144d333bb6a)
[![DOI](https://zenodo.org/badge/99702514.svg)](https://zenodo.org/badge/latestdoi/99702514)

[![Python (pip) build](https://github.com/virgesmith/UKCensusAPI/actions/workflows/py-build-test.yml/badge.svg)](https://github.com/virgesmith/UKCensusAPI/actions/workflows/py-build-test.yml)
[![R-CMD-check](https://github.com/virgesmith/UKCensusAPI/actions/workflows/R-build-test.yml/badge.svg)](https://github.com/virgesmith/UKCensusAPI/actions/workflows/R-build-test.yml)

> ## Update
> This package has been something of a misnomer as it only used Nomisweb as its data source, which only provides full census data for England & Wales. (They do provide some UK key statistics and quick statistics tables).

> Version 1.1.x of this package extends the 2011 census data coverage for Scotland and Northern Ireland. The aim is to make the data (and the metadata) consistent across all nations, but as neither country provide a web API for their data we have to resort to web scraping. This means the slicing-and-dicing and geographical query functionality may be more limited than it is for England & Wales. Note also that category values in equivalent tables may differ slightly.

> ### Scotland
> For Scotland, data can be downloaded at country or Council Area (~LAD) level, at geographical resolutions of Council Area, Data Zone (~LSOA) and Output Area. Intermediate Area (~MSOA) data can be aggregated (only) where the data is available at a higher geographical resolution.

> The principal functions are `NRScotland.get_metadata()` for metadata, `NRScotland.get_data()` for the actual data, and `NRScotland.contextify()` to annotate the data using the metadata.

> **NB The OA-level Scotland data is provided in a zip compression format (deflate64) that python cannot extract. If this data is requested, you'll get an error message containing instructions on how to fix the issue by manually extracting the file(s) using unzip or 7zip.**

> ### Northern Ireland
> For Northern Ireland, data can be downloaded at country or Local Government District (~LAD) level, at geographical resolutions of Super Output Area (~LSOA) and Small Area (OA). Ward (~MSOA) (~MSOA) data can be aggregated (only) where the data is available at higher geographical resolution.
> The principal functions are `NISRA.get_metadata()` for metadata, `NISRA.get_data()` for the actual data, and `NISRA.contextify()` to annotate the data using the metadata.

[Nomisweb](https://www.nomisweb.co.uk), run by Durham University, provides online access to the most detailed and up-to-date statistics from official sources for local areas throughout the UK, including census data.

This package provides both a `python` and an `R` wrapper around the nomisweb census data API, the NRScotland and NISRA websites, enabling:

- querying table metadata
- autogenerating customised python and R query code for future use
- automated cached data downloads
- modifying the geography of queries
- adding descriptive information to tables (from metadata)

Queries can be customised on geographical coverage, geographical resolution, and table fields, the latter can be filtered to include only the category values you require.

The package can generate reusable code snippets that can be inserted into applications. Such applications will work seamlessly for any user as long as they have installed this package, and possess their own nomisweb API key.

Since census data is essentially static, it makes little sense to download the data every time it is requested: all data downloads are cached.

Example code is also provided which:
- shows how an existing query can easily be modified in terms of geographical coverage.
- shows how raw data can be annotated with meaningful metadata

## Prerequisites

### Software

- python3.4 or higher, with pip, numpy and pandas. The dependencies should install automatically. Python 2 is not supported.
- R version 3.3.3 or higher (optional, if using the R interface)

### API key

It is recommended that you register with [nomisweb](https://www.nomisweb.co.uk) before using this package and use the API key the supply you in all queries. Without a key, queries will be truncated (max 25000 rows). With a key, the row limit is 1000000 and this package will warn if a query generates data with this number of rows.

Once registered, you will find your API key on [this page](https://www.nomisweb.co.uk/myaccount/webservice.asp). You should not divulge this key to others.

This package will look for the key in the following places (in order):
- locally: a file `NOMIS_API_KEY` in the cache directory defined at initialisation, e.g.
   ```
   $ cat cache/NOMIS_API_KEY
   0x0000000000000000000000000000000000000000
   ```
- globally: the environment variable NOMIS_API_KEY. R users can store the key in their `.Renviron` file: R will set the environment on startup, which will be visible to a python session instantiated from R.

Initialisation will fail if the key is not defined in one of these locations. Note: if for some reason you cannot register with nomisweb, you must still define an API key - just set it to an obviously invalid value.

## Installation

### python (from PyPI)
```
user@host:~$ python3 -m pip install UKCensusAPI
```
(NB This will install only the core package without the examples.)

### python (from conda-forge)
```bash
$ conda install -c conda-forge ukcensusapi
```
(NB This will install only the core package without the examples.)

### python (from github)
```
user@host:~$ pip install git+https://github.com/virgesmith/UKCensusAPI.git
```
### python (from cloned repo):
```
user@host:~/dev/UKCensusAPI$ ./setup.py install
```
and to test
```
user@host:~/dev/UKCensusAPI$ ./setup.py test
```
### R
```
> devtools::install_github("virgesmith/UKCensusAPI")
```
Set the `RETICULATE_PYTHON` environment variable in your .Renviron file to the python3 interpreter, e.g. (for linux)
```
RETICULATE_PYTHON=$(which python3)
```

## Usage

In your Python code import the package like e.g.:
```
import ukcensusapi.Nomisweb as census_api
```
And in R:
```
library(UKCensusAPI)
```
### Queries

Queries have three distinct subtypes:

- metadata: query a table for the fields and categories it contains
- geography: retrieve a list of area codes of a particular type within a given region of another (larger) type.
- data: retrieve data from a table using a query built from the metadata and geography.

Data and metadata are cached locally to minimise requests to the data providers.

Using the interactive query builder, and a known table, you can construct a programmatically reusable query selecting categories, specific category values, and (optionally) geography, See example below.

Queries can subsequently be programmatically modified to switched to a different geographical region and/or resolution.

### Interactive Query

The first thing users may want to do is an interactive query. All you need to do is specify the name of a census table. The script will then iterate over the categories within the table, prompting you user to select the categories and values you're interested in.

Once done you'll be prompted to (optionally) specify a geography for the data - a geographical region and a resolution.

Finally, if you've specified the geography, the script will ask if you want to download (and cache) the data immediately.

This can be run using this script:
```bash
$ ukcensus-query <cache-dir> [--no-api-key]
```
An API key must be specified (see [above](#api-key)) unless the `--no-api-key` flag has been set.

The script will produce the following files (in the supplied cache directory):

- a json file containing the table metadata
- python and R code snippets that build the query and call this package to download the data
- (optionally, depending on above selections) the data itself

The code snippets are designed to be copy/pasted into user code. The (cached) data and metadata can simply be loaded by user code as required.

Note for R users - there is no direct R script for the interactive query largely due to the fact it will not work from within RStudio (due to the way RStudio handles stdin).

### Data reuse

Existing cached data is always used in preference to downloading. The data is stored locally using a filename based on the table name and md5 hash of the query used to download the data. This way, different queries on the same table can be stored.

To force the data to be downloaded, just delete the cached data.

### Query Reuse

The code snippets can simply be inserted into user code, and the metadata (json) can be used as a guide for modifying the query, either manually or automatically.

### Switching Geography

Existing queries can easily be modified to switch to a different geographical area and/or a different geographical resolution.

This allows, for example, users to write models where the geographical coverage and resolution can be user inputs.

Examples of how to do this are in [`geoquery.py`](inst/examples/geoquery.py) and [`geoquery.R`](inst/examples/geoquery.R).

### Annotating Data

Queries will download data with a minimal memory footprint, but also metadata that provides meaning. Whilst this makes manipulating and querying the data efficient, it means that the data itself lacks human-readability. For this reason the package provides a way of annotating tables with contextual data derived from the table metadata.

Examples of how to do this are in [`contextify.py`](inst/examples/contextify.py) and [`contextify.R`](inst/examples/contextify.R).

## Interactive Query Builder

This functionality requires that you already know the name of the census table of interest, and want to define a custom query on that table, for a specific geography at a specific resolution.

If you're unsure about which table to query, Nomisweb provide a useful [table finder](https://www.nomisweb.co.uk/census/2011/data_finder). NB Not all census tables are available at all geographical resolutions, but the above link will enumerate the available resolutions for each table.

### Interactive Query - Example

Run the script. You'll be prompted to enter the name of the census table of interest:

<pre>
$ ukcensus-query .
Nomisweb census data interactive query builder
See README.md for details on how to use this package
Census table: <b>KS401EW</b>
KS401EW - Dwellings, household spaces and accommodation type
</pre>

The table description is displayed. The script then iterates through the available fields and you are prompted to select the categories you require. For the purposes of this example let's say we only want a subset of the fields: just some of the dwelling types. Required values should be comma separated, or where contiguous, separated by '...'.

<pre>
CELL:
  0 (All categories: Dwelling type)
  1 (Unshared dwelling)
  2 (Shared dwelling: Two household spaces)
  3 (Shared dwelling: Three or more household spaces)
  4 (All categories: Household spaces)
  5 (Household spaces with at least one usual resident)
  6 (Household spaces with no usual residents)
  7 (Whole house or bungalow: Detached)
  8 (Whole house or bungalow: Semi-detached)
  9 (Whole house or bungalow: Terraced (including end-terrace))
  10 (Flat, maisonette or apartment: Purpose-built block of flats or tenement)
  11 (Flat, maisonette or apartment: Part of a converted or shared house (including bed-sits))
  12 (Flat, maisonette or apartment: In a commercial building)
  13 (Caravan or other mobile or temporary structure)
Select categories (default 0): <b>7...13</b>
</pre>
Select the output type you want (absolute values or percentages)
<pre>
MEASURES:
  20100 (value)
  20301 (percent)
Select categories (default 0): <b>20100</b>
</pre>
For the purposes of this example we don't require the RURAL_URBAN field in our output, so we just hit return to accept the default selection. When the default is selected, the query builder will prompt you for whether you want to include this field in the output. (If something other than the default is not selected, the query builder will always assume that you want the field in the output.)
<pre>
RURAL_URBAN:
  0 (Total)
  1 (Urban city and town in a sparse setting)
  2 (Urban major conurbation)
  3 (Urban minor conurbation)
  4 (Urban city and town)
  101 (Rural (total))
  6 (Rural village in a sparse setting)
  7 (Rural hamlet and isolated dwellings in a sparse setting)
  8 (Rural town and fringe)
  9 (Rural village)
  10 (Rural hamlet and isolated dwellings)
  100 (Urban (total))
  5 (Rural town and fringe in a sparse setting)
Select categories (default 0): <b>&#8629;</b>
include in output? (y/n) <b>n</b>
</pre>
Now you can optionally select the geographical area(s) you want to cover. This can be a single local authority, multiple local authorities, England, England & Wales, GB or UK. If a local authority, you can specify it either by name or ONS code (e.g. E09000001)
<pre>
Add geography? (y/N): <b>y</b>

Geographical coverage
E/EW/GB/UK or LA code(s)/name(s), comma separated: <b>Leeds</b>
</pre>
All the available geographies for the data are displayed. Select the geographical resolution required.
<pre>
TYPE265 NHS area teams
TYPE266 clinical commissioning groups
TYPE267 built-up areas including subdivisions
TYPE269 built-up areas
TYPE273 national assembly for wales electoral regions 2010
TYPE274 postcode areas
TYPE275 postcode districts
TYPE276 postcode sectors
TYPE277 national assembly for wales constituencies 2010
TYPE279 parishes 2011
TYPE282 2011 local health boards
TYPE283 2011 primary care trusts
TYPE284 2011 strategic health authorities
TYPE295 2011 wards
TYPE297 2011 super output areas - middle layer
TYPE298 2011 super output areas - lower layer
TYPE299 2011 output areas
TYPE459 local enterprise partnerships (as of April 2017)
TYPE460 parliamentary constituencies 2010
TYPE462 former metropolitan counties
TYPE463 local authorities: county / unitary (prior to April 2015)
TYPE464 local authorities: district / unitary (prior to April 2015)
TYPE480 regions
TYPE499 countries
Select Resolution: <b>TYPE297</b>
</pre>

You will then be prompted to choose whether to download the data immediately. If so, the query builder assembles the query and computes an md5 hash of it. It then checks the cache directory if a file with this name exists and will load the data from the file if so. If not, the query builder downloads the data and save the data in the cache directory.
```
Get data now? (y/N): y

Getting data...

Writing python code snippet to KS401EW.py

Writing R code snippet to KS401EW.R
$
```
Regardless of whether you selected geography, or downloaded the data, the query builder will generate python and R code snippets for later use.

The generated python code snippet is:

```
"""
KS401EW - Dwellings, household spaces and accommodation type

Code autogenerated by UKCensusAPI
(https://github.com/virgesmith/UKCensusAPI)
"""

# This code requires an API key, see the README.md for details

# Query url:
# https://www.nomisweb.co.uk/api/v01/dataset/NM_618_1.data.tsv?CELL=7...13&MEASURES=20100&RURAL_URBAN=0&date=latest&geography=1245714681...1245714688&select=GEOGRAPHY_CODE%2CCELL%2COBS_VALUE

import ukcensusapi.Nomisweb as CensusApi

api = CensusApi.Nomisweb("/tmp/UKCensusAPI/")
table = "KS401EW"
table_internal = "NM_618_1"
query_params = {}
query_params["RURAL_URBAN"] = "0"
query_params["select"] = "GEOGRAPHY_CODE,CELL,OBS_VALUE"
query_params["date"] = "latest"
query_params["geography"] = "1245714681...1245714688"
query_params["MEASURES"] = "20100"
query_params["CELL"] = "7...13"
KS401EW = api.get_data(table, table_internal, query_params)
```
The the R code:
```
# KS401EW - Dwellings, household spaces and accommodation type

# Code autogenerated by UKCensusAPI
#https://github.com/virgesmith/UKCensusAPI

# This code requires an API key, see the README.md for details
# Query url: https://www.nomisweb.co.uk/api/v01/dataset/NM_618_1.data.tsv?CELL=7...13&MEASURES=20100&RURAL_URBAN=0&date=latest&geography=1245714681...1245714688&select=GEOGRAPHY_CODE%2CCELL%2COBS_VALUE

library("UKCensusAPI")
cacheDir = "/tmp/UKCensusAPI/"
api = UKCensusAPI::instance(cacheDir)
table = "KS401EW"
table_internal = "NM_618_1"
queryParams = list(
  RURAL_URBAN = "0",
  select = "GEOGRAPHY_CODE,CELL,OBS_VALUE",
  date = "latest",
  geography = "1245714681...1245714688",
  MEASURES = "20100",
  CELL = "7...13"
)
KS401EW = UKCensusAPI::getData(api, table, table_internal, queryParams)
```
Users can then copy and paste the generated code snippets into their models, modifying as necessary, to automate the download of the correct data. The metadata looks like this:

```
{
  "nomis_table": "NM_618_1",
  "description": "KS401EW - Dwellings, household spaces and accommodation type",
  "fields": {
    "GEOGRAPHY": {
      "2092957703": "England and Wales",
      "2092957699": "England",
      "2092957700": "Wales"
    },
    "RURAL_URBAN": {
      "0": "Total",
      "100": "Urban (total)",
      "2": "Urban major conurbation",
      "3": "Urban minor conurbation",
      "4": "Urban city and town",
      "1": "Urban city and town in a sparse setting",
      "101": "Rural (total)",
      "8": "Rural town and fringe",
      "5": "Rural town and fringe in a sparse setting",
      "9": "Rural village",
      "6": "Rural village in a sparse setting",
      "10": "Rural hamlet and isolated dwellings",
      "7": "Rural hamlet and isolated dwellings in a sparse setting"
    },
    "CELL": {
      "0": "All categories: Dwelling type",
      "1": "Unshared dwelling",
      "2": "Shared dwelling: Two household spaces",
      "3": "Shared dwelling: Three or more household spaces",
      "4": "All categories: Household spaces",
      "5": "Household spaces with at least one usual resident",
      "6": "Household spaces with no usual residents",
      "7": "Whole house or bungalow: Detached",
      "8": "Whole house or bungalow: Semi-detached",
      "9": "Whole house or bungalow: Terraced (including end-terrace)",
      "10": "Flat, maisonette or apartment: Purpose-built block of flats or tenement",
      "11": "Flat, maisonette or apartment: Part of a converted or shared house (including bed-sits)",
      "12": "Flat, maisonette or apartment: In a commercial building",
      "13": "Caravan or other mobile or temporary structure"
    },
    "MEASURES": {
      "20100": "value",
      "20301": "percent"
    },
    "FREQ": {
      "A": "Annually"
    }
  },
  "geographies": {
    "TYPE265": "NHS area teams",
    "TYPE266": "clinical commissioning groups",
    "TYPE267": "built-up areas including subdivisions",
    "TYPE269": "built-up areas",
    "TYPE273": "national assembly for wales electoral regions 2010",
    "TYPE274": "postcode areas",
    "TYPE275": "postcode districts",
    "TYPE276": "postcode sectors",
    "TYPE277": "national assembly for wales constituencies 2010",
    "TYPE279": "parishes 2011",
    "TYPE282": "2011 local health boards",
    "TYPE283": "2011 primary care trusts",
    "TYPE284": "2011 strategic health authorities",
    "TYPE295": "2011 wards",
    "TYPE297": "2011 super output areas - middle layer",
    "TYPE298": "2011 super output areas - lower layer",
    "TYPE299": "2011 output areas",
    "TYPE459": "local enterprise partnerships (as of April 2017)",
    "TYPE460": "parliamentary constituencies 2010",
    "TYPE462": "former metropolitan counties",
    "TYPE463": "local authorities: county / unitary (prior to April 2015)",
    "TYPE464": "local authorities: district / unitary (prior to April 2015)",
    "TYPE480": "regions",
    "TYPE499": "countries"
  }
}
```
If you've selected to download the data, a tsv file (like csv but with a tab separator) called `KS401EW_8a13b34bade69f230b62ce0875c47437.tsv` will be saved in the cache directory:

```
"GEOGRAPHY_CODE"	"CELL"	"OBS_VALUE"
"E02002330"	"7"	1736
"E02002330"	"8"	743
"E02002330"	"9"	224
"E02002330"	"10"	106
"E02002330"	"11"	13
"E02002330"	"12"	7
"E02002330"	"13"	0
"E02002331"	"7"	597
"E02002331"	"8"	797
...
```

The data in this table has (for brevity and efficiency) the values "7" to "13" in the cell column, which are obviously meaningless without context. Meaning can be conveyed using the metadata that is also downloaded and cached locally. It's probably best to leave this step until the result stage, but you can annotate a table, given a column name and the appropriate metadata, using the `contextify` function, like this:

```
"GEOGRAPHY_CODE"	"CELL"	"OBS_VALUE"	"CELL_NAME"
"E02002330"	"7"	1736	"Whole house or bungalow: Detached"
"E02002330"	"8"	743	"Whole house or bungalow: Semi-detached"
"E02002330"	"9"	224	"Whole house or bungalow: Terraced (including end-terrace)"
"E02002330"	"10"	106	"Flat, maisonette or apartment: Purpose-built block of flats or tenement"
"E02002330"	"11"	13	"Flat, maisonette or apartment: Part of a converted or shared house (including bed-sits)"
"E02002330"	"12"	7	"Flat, maisonette or apartment: In a commercial building"
"E02002330"	"13"	0	"Caravan or other mobile or temporary structure"
"E02002331"	"7"	597	"Whole house or bungalow: Detached"
"E02002331"	"8"	797	"Whole house or bungalow: Semi-detached"
...
```
See the example code in [contextify.py](inst/examples/contextify.py) and/or [contextify.R](inst/examples/contextify.R)

## Detailed Help

### Public classes/methods (python)

Use python's built-in help functionality, e.g.
```
>>> import ukcensusapi.Nomisweb as api
>>> help(api)
...
>>> import ukcensusapi.Query as query
>>> help(query)
```
### Public functions (R)

See the man pages, which can be accessed from RStudio using the command `?UKCensusAPI`

## Support and Feature Requests

Please use the issues section to report bugs, request features and see status of existing issues. Code contributions (by PR) are most welcome.



