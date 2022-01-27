# Anena Data Importer

This directory contains tools to import data from [ANENA](https://www.anena.org).

Anena XLS files (see https://www.anena.org/5041-bilan-des-accidents.htm) from 2010 to 2017 are
exported from the `Sphinx iQ2`
<https://www.lesphinx-developpement.fr/logiciels/enquete-analyse-sphinx-iq>`_ proprietary software.
Only 39 variables of the 139 are exported.

Since theses data need to be prepared, we use `xlrd` instead of `pandas`.  In details:

* data are homogenised
* string enumerate values are translated to Python `Enum`
* column names are translated to English and in valid Python attribute
* dates and hours are merged to `datetime`
* rescue delays are converted to minutes
* coordinates are fixed
