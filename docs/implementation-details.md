# Implementation Details

## JSON Accident Report Format

This project implements a [JSON](https://www.json.org/json-en.html) accident report format to store
accident data.  JSON is a text format based on a subset of the JavaScript Programming Language
Standard ECMA-262 3rd Edition - December 1999.  JSON is a data standard on the web and is also used
by the SERAC API of [camptocamp](https://www.camptocamp.org/serac).

Thanks to [Pydantic](https://pydantic-docs.helpmanual.io/usage/schema/), a JSON schema can be
automatically generated from the code.

## Software Dependencies

* [Matplotlib](https://matplotlib.org) a comprehensive library for creating static, animated, and interactive visualisations.
  Matplotlib is used to generate publication quality figures.
* [Numpy](https://numpy.org) a fundamental package for scientific computing.
* [requests](https://docs.python-requests.org/en/latest) a simple HTTP library
* [Pandas](https://pandas.pydata.org) a fast, powerful, flexible and easy to use open source data
  analysis and manipulation tool, built on top of the Python programming language.
* [pydantic](https://pydantic-docs.helpmanual.io) Data validation using python type annotations.
* [pyproj](https://pyproj4.github.io/pyproj/stable) interface to [PROJ](https://proj.org) (cartographic projections and coordinate transformations library)
* [xlrd](https://github.com/python-excel/xlrd) a library for reading data from Excel files in the historical .xls format.
  [doc](https://xlrd.readthedocs.io/en/latest)
  see also https://www.python-excel.org and [openpyxl](https://openpyxl.readthedocs.io/en/stable)

## Interesting Software
