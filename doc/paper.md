---
title: 'UKCensusAPI: python and R interfaces to the nomisweb UK census data API'
tags:
  - python
  - r
  - data science
authors:
 - name: Andrew P Smith
   orcid: 0000-0002-9951-6642
   affiliation: 1
affiliations:
 - name: School of Geography and Leeds Institute for Data Analytics, University of Leeds
   index: 1
date: 6 September 2017
bibliography: paper.bib
---

# Summary

Nomisweb [@noauthor_nomis_nodate] provide an extremely useful API for querying and downloading UK census data. However, in practice data queries must be built manually and the query URL copied and pasted into user code. This makes modification of queries laborious and this is especially so when (re)defining the geographical coverage and resolution of a query.

This package [@smith_ukcensusapi:_2017] provides both python and R interfaces around the nomisweb API that address these shortcomings. It contains functionality to:
- query tables directly for their metadata
- autogenerate customised python and R query code for reuse
- automate and cache data and metadata downloads
- easily modify the geographical coverage and resolution of existing queries
- add descriptive information to downloaded tables (from metadata)

This is particularly useful in applications such as microsimulation, where there are requirements to run the model for different geographical areas and/or different geographical resolutions with minimal user/developer intervention.

# References
