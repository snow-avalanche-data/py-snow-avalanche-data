# Description

The aims of this project is to perform [Reproducible
Research](https://esajournals.onlinelibrary.wiley.com/doi/full/10.1002/bes2.1801) on snow avalanche
accident data.

The analysis tool is written in [Python](https://www.python.org) language and is based on libraries
which are part of the [ecosystem for scientific computing with Python](https://numpy.org).  All the
components of this framework are open source and free of charge.

The source code is licensed under the [GNU Affero General Public
License](https://www.gnu.org/licenses/agpl-3.0.en.html).

This repository contains also some French snow avalanche accident data stored in
[JSON](https://www.json.org/json-en.html).

* [Contribution guidelines for this project](docs/CONTRIBUTING.md)
* [Origin of the data](docs/accident-data.md)
* [Note on the code](implementation-details.md)

# TODO List

* look at https://pydantic-docs.helpmanual.io
* merge c2c client code

# Features

The source code features

* a module to implement an JSON format for accident
* a module to perform introspection on JSON DATA and generate a schema
* a module to import ANENA xls files
* a module to implement a client to connect to the C2C API
* a module to work with SERAC data
* a module to perform statistical analyses
* a module to generate plots

# About Authors

* **Fabrice SALVAIRE** holds a PhD in data analysis in high energy physics, works as computer
  scientist, and perform climbing, mountaineering and ski touring during his free time (affiliated
  to the sports federation [FSGT/ROC14](https://www.fsgt.org/activites/escal_mont)).
