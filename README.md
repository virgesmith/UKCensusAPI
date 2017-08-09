# UK Census Data API

[![Build Status](https://travis-ci.org/virgesmith/UKCensusAPI.png?branch=master)](https://travis-ci.org/virgesmith/UKCensusAPI) [![License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://opensource.org/licenses/MIT)

This package provides a wrapper around the nomisweb census data API, enabling automated downloads of data.

The code is primarily written in python, but we also supply an R interface for convenience. 

It is recommended that you register with [nomisweb](https://www.nomisweb.co.uk) before using this package and use the API key the supply you in all queries. Without a key, queries may be truncated.

Once registered, you will find your API key on [this page](https://www.nomisweb.co.uk/myaccount/webservice.asp). You should not divulge this key to others.

The python code expects the key to be defined in an environment variable, like so:

```
user@host:~$ echo $NOMIS_API_KEY
0x0000000000000000000000000000000000000000
```
where as for R, as is standard practice, the key is stored in the user's environment:

```
user@host:~$ grep NOMIS_API_KEY ~/.Renviron 
NOMIS_API_KEY=0x0000000000000000000000000000000000000000
```

This avoids hard-coding the API key into code, which could easily end up in a publically accessible repo.

Queries can be customised on geographical coverage, geographical resolution, and table fields, the latter can be filtered to include only the category values you require.

Since census data is essentially static, it makes little sense to download the data every time it is requested: all data downloads are cached.

## Usage

The general usage model is a two-step process. Firstly users can execute a one-off interactive query where the user specifies:
- a census table, 
- geographical coverage and resolution
- the fields and categories required in the output
This produces:
- the data itself in the cache directory
- python and R code 

This produces reusable code, and second step is to insert the generated code above into models that require the data. 

Another important usage example is to be able to easily switch a model to a different geographical area and/or a different geographical resolution by modifying an existing query whilst still using the same table data. In this case only the 'geography' element of the query changes. Non-interactive examples are provided for this in `geoquery.py`

#### Code

- `NomiswebApi.py` - python class containing the API functionality 
- `NomiswebApi.R` - R equivalent of above
- `interactive.py` - interactive python script for building queries and downloading data for later use, can be called from R

Queries have three distinct subtypes:
- metadata: query a table for the fields and categories it contains
- geographic: retrieve a list of area codes of a particular type within a given region of another (larger) type. 
- data: retrieve data from a table using a query built from the metadata and geography.

Data is cached locally to avoid unnecessary requests to nomisweb.co.uk.

Using the interactive query builder, and a known table, you can select geography, categories and category values. The code will assemble the query, then download and cache the data.

The query builder also prints python code that can be subsequently used in a non-interactive application that requires the data.

#### NomiswebApi python Class

This class handles:
- conversion from ONS table names geographical codes to the nomisweb internal equivalents.
- compression of geographic code lists into the shortest possible form (to minimise http header size issues).
- metadata, geographical, and data queries.
- appending the user's API key to queries.
- retrieving and cacheing of data.

The class (currently) depends on a local data file `laMapping.csv` that maps local authority names to nomis internal codes.

The class constructor requires you so specify a location for a cache directory and well as the file above.

### NomiswebApi R functions

Provides the basic functionality to fetch data given a precompiled query, for querying tables for their metadata, and for generating new geographic coverage and resolution for modifying existing queries. 

### Interactive Query Builder

This functionality requires that you already know the name of the census table of interest, and want to define a custom query on that table, for a specific geography at a specific resolution.

If you're unsure about which table to query, Nomisweb provide a useful [table finder](https://www.nomisweb.co.uk/census/2011/data_finder). NB Not all census tables are available at all geographical resolutions, but the above link will enumerate the available resolutions for each table.


#### Example

Run the script. You'll be prompted to enter the name of the census table of interest:

<pre>
user@host:~/dev/Mistral/python$ ./interactive.py 
Nomisweb census data interactive query builder
See README.md for details on how to use this package
Census table: <b>KS401EW</b>
</pre>
Now select the geographical area(s) you want to cover. This can be a single local authority, multiple local authorities, England, England & Wales, GB or UK.
<pre>
Coverage
E/EW/GB/UK or LA name(s), comma separated: <b>Leeds</b>
</pre>
Now select the geographical resolution required. Currently supports local authority, MSOA, LSOA, and OA:
<pre>
Resolution (LA/MSOA/LSOA/OA): <b>MSOA</b>
</pre>
The table description is displayed. The script then interates through the available fields.
```
KS401EW - Dwellings, household spaces and accommodation type
```
You are now prompted to select the categories you require. For the purposes of this example let's say we only want a subset of the fields. Required values should be comma separated, or where contiguous, separated by '...'.

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
The query builder assembles the query and computes an md5 hash of it. It then checks the cache directory if a file with this name exists and will load the data from the file if so. If not, the query builder downloads the data and save the data in the cache directory. 

```
Getting data...
Downloading and cacheing data: ../data/b8b663a9d3fb331a9612aee2d3203c57.tsv

Writing python code to KS401EW.py

Writing R code to KS401EW.R
user@host:~$
```
User can then copy and paste the generated code snippets into their models, modifying as necessary, to automate the download of the correct data.
The generated python code snippet is:

```
# KS401EW - Dwellings, household spaces and accommodation type

# Code autogenerated by NomiswebApi

# This code requires an API key, see the README.md for details

# Query url:
# https://www.nomisweb.co.uk/api/v01/dataset/NM_618_1.data.tsv?CELL=7...13&MEASURES=20100&RURAL_URBAN=0&date=latest&geography=1245710558...1245710660%2C1245714998...1245714998%2C1245715007...1245715007%2C1245715021...1245715022&select=GEOGRAPHY_CODE%2CCELL%2COBS_VALUE

from NomiswebApi import NomiswebApi
from collections import OrderedDict
api = NomiswebApi("../data/", "../persistent_data/laMapping.csv")
table = "NM_618_1"
queryParams = {}
queryParams[CELL] = "7...13"
queryParams[date] = "latest"
queryParams[RURAL_URBAN] = "0"
queryParams[select] = "GEOGRAPHY_CODE,CELL,OBS_VALUE"
queryParams[geography] = "1245710558...1245710660,1245714998...1245714998,1245715007...1245715007,1245715021...1245715022"
queryParams[MEASURES] = "20100"
KS401EW = api.getData(table, queryParams)

```
The the R code:
```
# KS401EW - Dwellings, household spaces and accommodation type

# Code autogenerated by NomiswebApi

# This code requires an API key, see the README.md for details

source("NomiswebApi.R")
cacheDir = "../data/"
queryUrl = "https://www.nomisweb.co.uk/api/v01/dataset/NM_618_1.data.tsv?CELL=7...13&MEASURES=20100&RURAL_URBAN=0&date=latest&geography=1245710558...1245710660%2C1245714998...1245714998%2C1245715007...1245715007%2C1245715021...1245715022&select=GEOGRAPHY_CODE%2CCELL%2COBS_VALUE"
KS401EW = NomiswebApi.getData(queryUrl, cacheDir)

```

