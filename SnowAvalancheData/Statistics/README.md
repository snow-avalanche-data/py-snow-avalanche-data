# Description

This directory contains codes to implements statistical tools, like histogram.

**Features**
* implements these bin width algorithms: Freedman-Diaconis, Knuth, Scott
  (Note: Bayesian blocks algorithm yields usually a too large bin width on our data)

# Bibliography

## Histogram

* https://root.cern.ch/root/htmldoc/guides/users-guide/Histograms.html
  Implements a histogram class with a fill method for huge dataset.
* https://docs.astropy.org/en/stable/api/astropy.stats.histogram.html#astropy.stats.histogram
  Implements these binning algorithms: Bayesian blocks for dynamic bin widths, Knuth, Scott, Freedman-Diaconis rule.
* https://numpy.org/doc/stable/reference/generated/numpy.histogram.html#numpy.histogram
* https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.rv_histogram.html
* https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.hist.html
* https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.hist.html
  https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.hist.html
