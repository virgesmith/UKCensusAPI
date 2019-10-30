"""
Data scraper for Scottish 2011 census Data
"""

import os.path
from pathlib import Path
import urllib.parse
import zipfile
import pandas as pd
import requests
import subprocess

import ukcensusapi.utils as utils


# Geographical area (EW equivalents)
# Council area (LAD)
# Intermediate zone (MSOA) ??
# Data zone (LSOA)
# Output area


# assumes all areas in coverage are the same type
def _coverage_type(code):
    if isinstance(code, list):
        code = code[0]
    if code == "S92000003":
        return "ALL"
    elif code[:3] == "S12":
        return "LAD"
    elif code[:3] == "S02":
        return "MSOA11"
    elif code[:3] == "S01":
        return "LSOA11"
    elif code[:3] == "S00":
        return "OA11"
    else:
        raise ValueError("Invalid code: {}".format(code))


class NRScotland:
    """
    NRScotland web data scraper.
    """

    #   ['S92000003' Scotland
    #   Council areas: 'S12000005' 'S12000006' 'S12000008' 'S12000010' 'S12000011'
    #   'S12000013' 'S12000014' 'S12000015' 'S12000017' 'S12000018' 'S12000019'
    #  'S12000020' 'S12000021' 'S12000023' 'S12000024' 'S12000026' 'S12000027'
    #  'S12000028' 'S12000029' 'S12000030' 'S12000033' 'S12000034' 'S12000035'
    #  'S12000036' 'S12000038' 'S12000039' 'S12000040' 'S12000041' 'S12000042'
    #  'S12000044' 'S12000045' 'S12000046']

    # static constants
    URL = "https://www.scotlandscensus.gov.uk/ods-web/download/getDownloadFile.html"

    data_sources = ["Council Area blk", "SNS Data Zone 2011 blk", "Output Area blk"]

    GeoCodeLookup = {
        # give meaning to some common nomis geography types/codes
        "LAD": 0,  # "Council Area blk", ,
        # MSOA (intermediate zone)?
        "LSOA11": 1,  # "SNS Data Zone 2011 blk"
        "OA11": 2,  # "Output Area blk"
    }

    SCGeoCodes = ["CA", "DZ", "OA"]

    # initialise, supplying a location to cache downloads
    def __init__(self, cache_dir):
        """Constructor.
        Args:
            cache_dir: cache directory
        Returns:
            an instance.
        """
        # checks exists and is writable, creates if necessary
        self.cache_dir = utils.init_cache_dir(cache_dir)

        self.offline_mode = not utils.check_online("https://www.scotlandscensus.gov.uk/ods-web/data-warehouse.html")
        if self.offline_mode:
            print("Unable to contact %s, operating in offline mode - pre-cached data only" % self.URL)

        # download the lookup if not present
        lookup_file = self.cache_dir / "sc_lookup.csv"
        if not os.path.isfile(str(lookup_file)):
            lookup_url = "https://www2.gov.scot/Resource/0046/00462936.csv"
            response = requests.get(lookup_url)
            response.raise_for_status()
            with open(str(lookup_file), 'wb') as fd:
                for chunk in response.iter_content(chunk_size=1024):
                    fd.write(chunk)

        self.area_lookup = pd.read_csv(str(self.cache_dir / "sc_lookup.csv"))

        # TODO use a map (just in case col order changes)
        self.area_lookup.columns = ["OA11", "LSOA11", "MSOA11", "LAD"]

    def get_geog(self, coverage, resolution):
        """
        Returns all areas at resolution in coverage
        """
        # assumes all areas in coverage are the same type
        coverage_type = _coverage_type(coverage)
        if coverage_type == "ALL":
            return self.area_lookup[resolution].unique()

        # ensure list
        if isinstance(coverage, str):
            coverage = [coverage]

        return self.area_lookup[self.area_lookup[coverage_type].isin(coverage)][resolution].unique()

    def get_metadata(self, table, resolution):
        """
        Returns the table metadata
        """
        return self.__get_rawdata(table, resolution)[0]

    def __get_rawdata(self, table, resolution, clear_cache=True):
        """
        Gets the raw csv data and metadata
        """

        zip_path = self.__source_to_zip(NRScotland.data_sources[NRScotland.GeoCodeLookup[resolution]])
        table_csv_path = self.cache_dir / str(table + '.csv')

        if clear_cache and os.path.isfile(table_csv_path):
            os.remove(table_csv_path)

        if not os.path.isfile(table_csv_path):
            print('Extracting {}'.format(str(table_csv_path)))
            subprocess.check_output(['7z', 'e', str(zip_path), str(table + '.csv'), '-o'+str(self.cache_dir)])

        raw_data = pd.read_csv(table_csv_path)

        # more sophisticate way to check for no data?
        if raw_data.shape == (2, 1):
            raise ValueError("Table {}: data not available at {} resolution.".format(table, resolution))
        # assumes:
        # - first column is geography (unnamed)
        # - any subsequent columns are categorical
        # - named columns are categories
        raw_cols = raw_data.columns.tolist()
        fields = {}

        col_index = 1
        while raw_cols[col_index][:8] == "Unnamed:":
            # lists format better than numpy arrays
            fields[table + "_" + str(col_index) + "_CODE"] = raw_data[raw_cols[col_index]].unique().tolist()
            col_index = col_index + 1

        categories = raw_data.columns.tolist()[col_index:]
        fields[table + "_0_CODE"] = dict(zip(range(len(categories)), categories))

        meta = {"table": table,
                "description": "",
                "geography": resolution,
                "fields": fields
                }
        return meta, raw_data
        # print(data.head())

    def get_data(self, table, coverage, resolution, category_filters={}, r_compat=False):
        """
        Returns a table with categories in columns, filtered by geography and (optionally) category values
        If r_compat==True, instead of returning a pandas dataframe it returns a dict raw value data and column names
        that can be converted into an R data.frame
        """

        # No data is available for Intermediate zones (~MSOA) so we get Data Zone (LSOA) then aggregate
        msoa_workaround = False
        if resolution == "MSOA11":
            msoa_workaround = True
            resolution = "LSOA11"

        geography = self.get_geog(coverage, resolution)
        meta, raw_data = self.__get_rawdata(table, resolution)
        # Clean up the mess:
        # - some csv files contain numbers with comma thousands separators (!)
        # - rather than using 0 to represent zero, hyphen is used
        raw_data.replace("-", 0, inplace=True)
        raw_data.replace(",", "", inplace=True, regex=True)
        # assumes the first n are (unnamed) columns we don't want to melt, geography coming first: n = geog + num
        # categories - 1 (the one to melt)
        lookup = raw_data.columns.tolist()[len(meta["fields"]):]

        id_vars = ["GEOGRAPHY_CODE"]
        for i in range(1, len(meta["fields"])):
            id_vars.append(table + "_" + str(i) + "_CODE")
        cols = id_vars.copy()
        cols.extend(list(range(0, len(lookup))))

        raw_data.columns = cols
        raw_data = raw_data.melt(id_vars=id_vars)
        id_vars.extend([table + "_0_CODE", "OBS_VALUE"])
        raw_data.columns = id_vars

        # ensure OBS_VALUE is numeric
        raw_data["OBS_VALUE"] = pd.to_numeric(raw_data["OBS_VALUE"])

        # convert categories to numeric values
        for i in range(1, len(meta["fields"])):
            category_name = raw_data.columns[i]
            category_values = meta["fields"][category_name]
            # make sure metadata has same no. of categories
            assert len(category_values) == len(raw_data[category_name].unique())
            category_map = {k: v for v, k in enumerate(category_values)}
            raw_data[category_name] = raw_data[category_name].map(category_map)

        # geography (and category_filter) must be lists
        if isinstance(geography, str):
            geography = [geography]

        # filter by geography
        data = raw_data[raw_data.GEOGRAPHY_CODE.isin(geography)]

        # If we actually requested MSOA-level data, aggregrate the LSOAs within each MSOA
        if msoa_workaround:
            data = data.reset_index(drop=True)
            lookup = self.area_lookup[self.area_lookup.LSOA11.isin(data.GEOGRAPHY_CODE)]
            lookup = pd.Series(lookup.MSOA11.values, index=lookup.LSOA11).to_dict()
            data.GEOGRAPHY_CODE = data.GEOGRAPHY_CODE.map(lookup)
            cols = list(data.columns[:-1])  # [1:]#.remove("GEOGRAPHY_CODE")
            data = data.groupby(cols).sum().reset_index()

        # multi-category filters
        for category in category_filters:
            filter = category_filters[category]
            if isinstance(filter, int):
                filter = [filter]
            data = data[data[category].isin(filter)]

        data = data.reset_index(drop=True)
        if r_compat:
            return {"columns": data.columns.values, "values": data.values}
        else:
            return data

    # TODO this is very close to duplicating the code in Nomisweb.py - refactor
    def contextify(self, table, meta, colname):
        """
        Replaces the numeric category codes with the descriptive strings from the metadata
        """
        lookup = meta["fields"][colname]
        # convert list into dict keyed on list index
        mapping = {k: v for k, v in enumerate(lookup)}
        category_name = colname.replace("_CODE", "_NAME")

        table[category_name] = table[colname].map(mapping)

        return table

    def __source_to_zip(self, source_name):
        """
        Downloads if necessary and returns the name of the locally cached zip file of the source data (replacing spaces with _)
        """
        zip = self.cache_dir / (source_name.replace(" ", "_") + ".zip")
        if not os.path.isfile(str(zip)):
            # The URL must have %20 (not "+") for space
            scotland_src = NRScotland.URL + "?downloadFileIds=" + urllib.parse.quote(source_name)
            print(scotland_src, " -> ", self.cache_dir / zip, "...", end="")
            response = requests.get(scotland_src)
            response.raise_for_status()
            with open(str(zip), 'wb') as fd:
                for chunk in response.iter_content(chunk_size=1024):
                    fd.write(chunk)
            print("OK")
        return zip
