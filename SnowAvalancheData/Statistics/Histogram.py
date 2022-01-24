####################################################################################################
#
# Avalanche - 
# Copyright (C) 2021 Fabrice Salvaire
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

__all__ = [
    'Binning1D',
    'EnumHistogram',
    'Histogram',
    'Interval',
]

####################################################################################################

import numpy as np

from .Binning import Binning1D, Interval

####################################################################################################

class Histogram:

    ##############################################

    def __init__(self, binning: Binning1D) -> None:
        if isinstance(binning, Binning1D):
            self._binning = binning
        else:
            raise ValueError

        # init accumulators
        array_size = self._binning.array_size
        self._accumulator = np.zeros(array_size)
        self._sum_weight_square = np.zeros(array_size)
        self._errors = np.zeros(array_size)

        self._errors_are_dirty = True

    ##############################################

    def clone(self) -> 'Histogram':
        # Fixme: binnning.clone()
        histogram = self.__class__(self._binning)
        histogram += self
        return histogram

    ##############################################

    def bin_label(self, i: int):
        return ''

    ##############################################

    @property
    def binning(self) -> Binning1D:
        return self._binning

    @property
    def accumulator(self) -> np.ndarray:
        return self._accumulator

    ##############################################

    def __iadd__(self, obj: 'Histogram') -> 'Histogram':
        """Add a n histogram"""
        if self.is_consistent_with(obj):
            self._accumulator += obj._accumulator
            self._sum_weight_square += obj._sum_weight_square
        else:
            raise ValueError
        return self

    ##############################################

    def is_consistent_with(self, obj: 'Histogram') -> bool:
        return self._binning == obj._binning

    ##############################################

    def clear(self, value: float=.0) -> None:
        self._accumulator[:] = value
        self._sum_weight_square[:] = value**2
        self._errors_are_dirty = True

    ##############################################

    def fill(self, x: float, weight: float=1.) -> None:
        if weight < 0:
            raise ValueError
        i = self._binning.find_bin(x)
        self._accumulator[i] += weight
        # if weight == 1.: weight_square = 1.
        self._sum_weight_square[i] += weight**2
        self._errors_are_dirty = True

    ##############################################

    def compute_errors(self) -> None:
        if self._errors_are_dirty:
            self._errors = np.sqrt(self._sum_weight_square)

    ##############################################

    def get_bin_error(self, i: int) -> float:
        self.compute_errors()
        return self._errors[i]

    ##############################################

    def integral(self, interval=None, interval_x=None):
        return self._accumulator.sum()
        # Fixme: purpose ?
        # if interval is None and interval_x is None:
        #     return self._accumulator.sum()
        # else:
        #     if interval_x is not None:
        #         start = self.binning.find_bin(interval_x.inf)
        #         stop = self.binning.find_bin(interval_x.sup)
        #     else:
        #         start = interval.inf
        #         stop = interval.sup
        #     return self._accumulator[start:stop +1].sum(), Interval(start, stop)

    ##############################################

    def normalise(self, scale: float=1) -> None:
        self._accumulator /= self.integral()
        self._errors_are_dirty = True
        if scale != 1:
            self._accumulator *= scale

    ##############################################

    def to_graph(self, centred=True, non_null=True) -> tuple:
        self.compute_errors()

        binning = self._binning
        bin_slice = binning.bin_slice()

        y = np.copy(self._accumulator[bin_slice])
        y_errors = np.copy(self._errors[bin_slice])

        if centred:
            x = binning.bin_centers()
        else:
            x = binning.bin_lower_edges()

        x_errors = np.empty(x.shape)
        x_errors[:] = .5*binning.bin_width

        if non_null:
            indices = np.where(y != 0)
            x = x[indices]
            y = y[indices]
            x_errors = x_errors[indices]
            y_errors = y_errors[indices]

        return x, y, x_errors, y_errors

   ###############################################

    def __str__(self):
        binning = self._binning
        text = f"""
Histogram 1D
  interval: {binning._interval}
  number of bins: {binning._number_of_bins}
  bin width: {binning._bin_width:g}
"""
        for i in binning.bin_iterator(xflow=True):
            accumulator = self._accumulator[i]
            if accumulator == 0:
                continue
            text += '%3u %s %s = %g +- %g\n' % (
                i,
                self.bin_label(i),
                str(binning.bin_interval(i)),
                accumulator,
                self.get_bin_error(i),
            )
        return text

####################################################################################################

class EnumHistogram(Histogram):

    ##############################################

    def __init__(self, cls) -> None:
        # Fixme: private API
        self._map = cls._value2member_map_
        self._labels = [str(_).split('.')[1] for _ in cls]
        values = self._map.keys()
        inf = min(values)
        sup = max(values) +1
        binning = Binning1D(Interval(inf, sup), bin_width=1)
        super().__init__(binning)

    ##############################################

    @property
    def labels(self) -> list[str]:
        return self._labels

    ##############################################

    def fill(self, x, weight: float=1.) -> None:
        if x is not None:
            super().fill(x.value, weight)

    ##############################################

    def bin_label(self, i: int):
        try:
            return self._map[i]
        except KeyError:
            return ''

    ##############################################

    def to_graph(self):
        # Fixme: duplicated code
        self.compute_errors()

        binning = self._binning
        bin_slice = binning.bin_slice()

        y = np.copy(self._accumulator[bin_slice])
        y_errors = np.copy(self._errors[bin_slice])

        x = np.arange(binning.number_of_bins)

        return x, y, y_errors
