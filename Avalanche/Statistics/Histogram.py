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

    def bin_label(self, i: int):
        return ''

    ##############################################

    @property
    def binning(self) -> Binning1D:
        return self._binning

    ##############################################

    @property
    def accumulator(self) -> np.ndarray:
        return self._accumulator

    ##############################################

    def __iadd__(self, obj: 'Histogram') -> 'Histogram':
        """Add a n histogram"""
        if self.is_consistent_with(obj):
            self._accumulator += obj._accumulator
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
        if interval is None and interval_x is None:
            return self._accumulator.sum()
        else:
            if interval_x is not None:
                start = self.binning.find_bin(interval_x.inf)
                stop = self.binning.find_bin(interval_x.sup)
            else:
                start = interval.inf
                stop = interval.sup
            return self._accumulator[start:stop +1].sum(), Interval(start, stop)

    ##############################################

    def normalise(self, scale=1):
        self._accumulator /= self.integral()
        self._errors_are_dirty = True
        if scale != 1:
            self._accumulator *= scale

    ##############################################

    def to_graph(self):
        self.compute_errors()

        binning = self._binning
        bin_slice = binning.bin_slice()

        x_values = binning.bin_centers()

        y_values = np.copy(self._accumulator[bin_slice])
        y_errors = np.copy(self._errors[bin_slice])

        x_errors = np.empty(x_values.shape)
        x_errors[:] = .5*binning.bin_width

        return x_values, y_values, x_errors, y_errors

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
            text += '%3u %s %s = %g +- %g\n' % (
                i,
                self.bin_label(i),
                str(binning.bin_interval(i)),
                self._accumulator[i],
                self.get_bin_error(i),
            )
        return text

   ###############################################

    def find_non_zero_bin_range(self):
        inf = 0
        while self._accumulator[inf] == 0:
            inf += 1
        sup = len(self._accumulator) -1
        while self._accumulator[sup] == 0:
            sup -= 1
        return Interval(inf, sup)

   ###############################################

    def non_zero_bin_range_histogram(self):

        bin_range = self.find_non_zero_bin_range()
        print(bin_range)
        binning = self._binning.sub_binning(self._binning.sub_interval(bin_range))
        print(binning)
        histogram = self.__class__(binning)
        src_slice = slice(bin_range.inf, bin_range.sup +1)
        dst_slice = slice(binning.first_bin, binning.over_flow_bin)
        histogram._accumulator[dst_slice] = self._accumulator[src_slice]
        histogram._sum_weight_square[dst_slice] = self._sum_weight_square[src_slice]
        histogram._errors[dst_slice] = self._errors[src_slice]
        histogram.errors_are_dirty = False

        return histogram

####################################################################################################

class EnumHistogram(Histogram):

    ##############################################

    def __init__(self, cls) -> None:
        # Fixme: private API
        self._map = cls._value2member_map_
        values = self._map.keys()
        inf = min(values)
        sup = max(values)
        binning = Binning1D(Interval(inf, sup), bin_width=1)
        super().__init__(binning)

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
