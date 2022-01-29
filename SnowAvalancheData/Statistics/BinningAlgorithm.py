####################################################################################################
#
# SnowAvalancheData - 
# Copyright (C) 2022 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
####################################################################################################

"""Methods for selecting the bin width of histograms

"""

# Ported from the astroML project: https://www.astroml.or
# Licensed under a 3-clause BSD style license

####################################################################################################

import numpy as np

# from . import bayesian_blocks

####################################################################################################

__all__ = [
    'scott_bin_width',
    'freedman_bin_width',
    'knuth_bin_width',
]

####################################################################################################

def scott_bin_width(data: np.ndarray, return_bins: bool=False) -> float:
    r"""Return the optimal histogram bin width using Scott's rule

    Scott's rule is a normal reference rule: it minimizes the integrated mean squared error in the
    bin approximation under the assumption that the data is approximately Gaussian.

    Parameters
    ----------
    data : array-like, ndim=1
        observed (one-dimensional) data
    return_bins : bool, optional
        if True, then return the bin edges

    Returns
    -------
    width : float
        optimal bin width using Scott's rule
    bins : ndarray
        bin edges: returned if ``return_bins`` is True

    Notes
    -----
    The optimal bin width is

    .. math::
        \Delta_b = \frac{3.5\sigma}{n^{1/3}}

    where :math:`\sigma` is the standard deviation of the data, and :math:`n` is the number of data
    points [1]_.

    References
    ----------
    .. [1] Scott, David W. (1979). "On optimal and data-based histograms".
       Biometricka 66 (3): 605-610

    See Also
    --------
    knuth_bin_width
    freedman_bin_width

    """

    data = np.asarray(data)
    if data.ndim != 1:
        raise ValueError("data should be one-dimensional")

    number_of_elements = data.size
    sigma = np.std(data)

    dx = 3.5 * sigma / (number_of_elements ** (1 / 3))

    if return_bins:
        number_of_bins = np.ceil((data.max() - data.min()) / dx)
        number_of_bins = max(1, number_of_bins)
        bins = data.min() + dx * np.arange(number_of_bins + 1)
        return dx, bins
    else:
        return dx

####################################################################################################

def freedman_bin_width(data: np.ndarray, return_bins: bool=False) -> float:
    r"""Return the optimal histogram bin width using the Freedman-Diaconis rule

    The Freedman-Diaconis rule is a normal reference rule like Scott's
    rule, but uses rank-based statistics for results which are more robust
    to deviations from a normal distribution.

    Parameters
    ----------
    data : array-like, ndim=1
        observed (one-dimensional) data
    return_bins : bool, optional
        if True, then return the bin edges

    Returns
    -------
    width : float
        optimal bin width using the Freedman-Diaconis rule
    bins : ndarray
        bin edges: returned if ``return_bins`` is True

    Notes
    -----
    The optimal bin width is

    .. math::
        \Delta_b = \frac{2(q_{75} - q_{25})}{n^{1/3}}

    where :math:`q_{N}` is the :math:`N` percent quartile of the data, and
    :math:`n` is the number of data points [1]_.

    References
    ----------
    .. [1] D. Freedman & P. Diaconis (1981)
       "On the histogram as a density estimator: L2 theory".
       Probability Theory and Related Fields 57 (4): 453-476

    See Also
    --------
    knuth_bin_width
    scott_bin_width
    """
    data = np.asarray(data)
    if data.ndim != 1:
        raise ValueError("data should be one-dimensional")

    number_of_elements = data.size
    if number_of_elements < 4:
        raise ValueError("data should have more than three entries")

    v25, v75 = np.percentile(data, [25, 75])
    dx = 2 * (v75 - v25) / (number_of_elements ** (1 / 3))
    # Fixme: dx can be zero
    # if dx == 0:
    #     dx = 1

    if return_bins:
        inf, sup = data.min(), data.max()
        number_of_bins = max(1, np.ceil((sup - inf) / dx))
        # print(inf, sup, number_of_bins)
        try:
            bins = inf + dx * np.arange(number_of_bins + 1)
        except ValueError as exception:
            if 'Maximum allowed size exceeded' in str(exception):
                raise ValueError(
                    'The inter-quartile range of the data is too small: '
                    'failed to construct histogram with {} bins. '
                    'Please use another bin method, such as '
                    'bins="scott"'.format(number_of_bins + 1)
                )
            else:   # Something else  # pragma: no cover
                raise
        return dx, bins
    else:
        return dx

####################################################################################################

def knuth_bin_width(data: np.ndarray, return_bins: float=False, quiet: float=True) -> float:
    r"""Return the optimal histogram bin width using Knuth's rule.

    Knuth's rule is a fixed-width, Bayesian approach to determining the optimal bin width of a
    histogram.

    Parameters
    ----------
    data : array-like, ndim=1
        observed (one-dimensional) data
    return_bins : bool, optional
        if True, then return the bin edges
    quiet : bool, optional
        if True (default) then suppress stdout output from scipy.optimize

    Returns
    -------
    dx : float
        optimal bin width. Bins are measured starting at the first data point.
    bins : ndarray
        bin edges: returned if ``return_bins`` is True

    Notes
    -----
    The optimal number of bins is the value M which maximizes the function

    .. math::
        F(M|x,I) = n\log(M) + \log\Gamma(\frac{M}{2})
        - M\log\Gamma(\frac{1}{2})
        - \log\Gamma(\frac{2n+M}{2})
        + \sum_{k=1}^M \log\Gamma(n_k + \frac{1}{2})

    where :math:`\Gamma` is the Gamma function, :math:`n` is the number of data points, :math:`n_k`
    is the number of measurements in bin :math:`k` [1]_.

    References
    ----------
    .. [1] Knuth, K.H. "Optimal Data-Based Binning for Histograms".
       arXiv:0605197, 2006

    See Also
    --------
    freedman_bin_width
    scott_bin_width

    """

    # import here because of optional scipy dependency
    from scipy import optimize

    knuth_function = KnuthFunction(data)
    dx0, bins0 = freedman_bin_width(data, True)
    # print(dx0, bins0)
    number_of_bins = optimize.fmin(knuth_function, len(bins0), disp=not quiet)[0]
    bins = knuth_function.bins(number_of_bins)
    dx = bins[1] - bins[0]

    if return_bins:
        return dx, bins
    else:
        return dx

####################################################################################################

class KnuthFunction:

    r"""Class which implements the function minimized by knuth_bin_width

    Parameters
    ----------
    data : array-like, one dimension
        data to be histogrammed

    Notes
    -----
    the function F is given by

    .. math::
        F(M|x,I) = n\log(M) + \log\Gamma(\frac{M}{2})
        - M\log\Gamma(\frac{1}{2})
        - \log\Gamma(\frac{2n+M}{2})
        + \sum_{k=1}^M \log\Gamma(n_k + \frac{1}{2})

    where :math:`\Gamma` is the Gamma function, :math:`n` is the number of data points, :math:`n_k`
    is the number of measurements in bin :math:`k`.

    See Also
    --------
    knuth_bin_width

    """

    ##############################################

    def __init__(self, data: np.ndarray) -> None:
        self.data = np.array(data, copy=True)
        if self.data.ndim != 1:
            raise ValueError("data should be 1-dimensional")
        self.data.sort()
        self._number_of_elements = self.data.size

        # import here rather than globally: scipy is an optional dependency.
        # Note that scipy is imported in the function which calls this,
        # so there shouldn't be any issue importing here.
        from scipy import special

        # create a reference to gammaln to use in self.eval()
        self._gammaln = special.gammaln

    ##############################################

    def bins(self, number_of_bins: int) -> np.ndarray:
        """Return the bin edges given M number of bins"""
        return np.linspace(self.data[0], self.data[-1], int(number_of_bins) + 1)

    ##############################################

    def __call__(self, number_of_bins: int) -> float:
        return self.eval(number_of_bins)

    ##############################################

    def eval(self, number_of_bins: int) -> float:
        """Evaluate the Knuth function

        Parameters
        ----------
        M : int
            Number of bins

        Returns
        -------
        F : float
            evaluation of the negative Knuth loglikelihood function:
            smaller values indicate a better fit.
        """

        M = int(number_of_bins)
        if M <= 0:
            return np.inf

        bins = self.bins(M)
        nk, bins = np.histogram(self.data, bins)
        N = self._number_of_elements

        return -(
            N * np.log(M)
            + self._gammaln(0.5 * M)
            - M * self._gammaln(0.5)
            - self._gammaln(N + 0.5 * M)
            + np.sum(self._gammaln(nk + 0.5))
        )
