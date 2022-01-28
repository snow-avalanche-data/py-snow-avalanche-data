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

####################################################################################################

__all__ = [
    'Binning1D',
    'BinningND',
    'Interval',
    'NDMixin',
]

####################################################################################################

from typing import Iterator

import numpy as np

from SnowAvalancheData.Statistics.IntervalArithmetic import Interval, FloatMinusInfinity, FloatPlusInfinity
from SnowAvalancheData.Statistics.Functions import rint

####################################################################################################

class Binning1D:

    UNDER_FLOW_BIN = 0
    FIRST_BIN = 1

    ##############################################

    def __init__(self, interval: Interval, bin_width: float=None, number_of_bins: int=None) -> None:

        if bin_width is None and number_of_bins is None:
            raise ValueError("...")

        self._interval = Interval(interval, right_open=True)
        if bin_width is not None:
            # Method to adjust the x range:
            #  - round sup, inf or both
            #  - extend sup, inf or both
            self._bin_width = float(bin_width)
            self._number_of_bins = rint(self._interval.length / self._bin_width)
            self._interval.sup = self._interval.inf + self._number_of_bins * self._bin_width
        else:
            self._number_of_bins = int(number_of_bins)
            self._bin_width = self._interval.length / self._number_of_bins

        self._last_bin = self._number_of_bins
        self._over_flow_bin = self._number_of_bins +1
        self._array_size = self._over_flow_bin +1

        self._inverse_bin_width = 1./self._bin_width

        # self._bin_centers = np.linspace(
        #     self.bin_center(self.FIRST_BIN),
        #     self.bin_center(self._last_bin),
        #     self._number_of_bins,
        # )

    ##############################################

    def clone(self) -> 'Binning1D':
        return self.__class__(self._interval, number_of_bins=self._number_of_bins)

    ##############################################

    def to_json(self) -> dict:
        return {
            'inf':self.interval.inf,
            'sup':self.interval.sup,
            'bin_width':self.bin_width,
        }

    ##############################################

    @classmethod
    def from_json(cls, data: dict) -> 'Binning1D':
        return cls(Interval(data['inf'], data['sup']), bin_width=data['bin_width'])

    ##############################################

    @property
    def interval(self) -> Interval:
        return self._interval

    @property
    def number_of_bins(self) -> int:
        return self._number_of_bins

    @property
    def under_flow_bin(self) -> int:
        return self.UNDER_FLOW_BIN

    @property
    def first_bin(self) -> int:
        return self.FIRST_BIN

    @property
    def last_bin(self) -> int:
        return self._over_flow_bin -1

    @property
    def over_flow_bin(self) -> int:
        return self._over_flow_bin

    @property
    def array_size(self) -> int:
        return self._array_size

    @property
    def bin_width(self) -> float:
        return self._bin_width

    # @property
    # def bin_centers(self):
    #     return self._bin_centers

    ##############################################

    def __eq__(self, other: 'Binning1D') -> bool:
        return (self._interval == other._interval
                and self._number_of_bins == other._number_of_bins)

   ###############################################

    def _check_bin_index(self, i: int, xflow: bool=False) -> None:
        if xflow:
            if self._over_flow_bin < i < self.UNDER_FLOW_BIN:
                raise IndexError
        else:
            if self._over_flow_bin <= i <= self.UNDER_FLOW_BIN:
                raise IndexError

    ##############################################

    def bin_interval(self, i: int) -> Interval:
        if i == self.UNDER_FLOW_BIN:
            return Interval(FloatMinusInfinity, self._interval.inf, left_open=True, right_open=True)
        elif i == self._over_flow_bin:
            return Interval(self._interval.sup, FloatPlusInfinity, right_open=True)
        else:
            return Interval(self.bin_lower_edge(i), self.bin_upper_edge(i), right_open=True)

   ###############################################

    def _bin_edge(self, i:int, offset: float=0) -> float:
        self._check_bin_index(i, xflow=False)
        return self._interval.inf + (i - 1 + offset)*self._bin_width

   ###############################################

    def bin_lower_edge(self, i: int) -> float:
        return self._bin_edge(i)

   ###############################################

    def bin_upper_edge(self, i: int) -> float:
        return self._bin_edge(i, offset=1)

   ###############################################

    def bin_center(self, i: int) -> float:
        return self._bin_edge(i, offset=.5)

    ##############################################

    def bins(self) -> np.ndarray:
        bins = np.zeros(self._number_of_bins +2)
        bins[self.UNDER_FLOW_BIN] = FloatMinusInfinity
        bins[self._over_flow_bin] = FloatPlusInfinity
        bins[self.FIRST_BIN:self.UNDER_FLOW_BIN] = \
            np.arange(
                start=self._interval.inf,
                stop=self._interval.sup + self._bin_width,
                step=self._bin_width,
            )
        return bins

    ##############################################

    def bin_lower_edges(self) -> np.ndarray:
        return np.linspace(
            self.bin_lower_edge(self.FIRST_BIN),
            self.bin_lower_edge(self._last_bin),
            self._number_of_bins,
        )

    ##############################################

    def bin_centers(self) -> np.ndarray:
        return np.linspace(
            self.bin_center(self.FIRST_BIN),
            self.bin_center(self._last_bin),
            self._number_of_bins,
        )

    ##############################################

    def bin_slice(self, xflow: bool=False) -> slice:
        if xflow:
            return slice(self.UNDER_FLOW_BIN, self._array_size)
        else:
            return slice(self.FIRST_BIN, self._over_flow_bin)

    ##############################################

    def bin_iterator(self, xflow: bool=False) -> Iterator[int]:
        if xflow:
            return range(self.UNDER_FLOW_BIN, self._array_size)
        else:
            return range(self.FIRST_BIN, self._over_flow_bin)

   ###############################################

    def find_bin(self, x: float) -> int:
        inf = self._interval.inf
        if x < inf:
            return self.UNDER_FLOW_BIN
        elif x >= self._interval.sup:
            return self._over_flow_bin
        else:
            return int(self._inverse_bin_width * (x - inf)) +1

   ###############################################

    def __str__(self) -> str:
        text = f"""
Binning 1D
  interval: {self._interval}
  number of bins: {self._number_of_bins}
  bin width: {self._bin_width:g}
"""
        for i in self.bin_iterator(xflow=True):
            # Fixme: 3u count number of digits
            text += '  %3u ' % i + str(self.bin_interval(i)) + '\n'
        return text

   ###############################################

    def sub_interval(self, bin_range: Interval) -> Interval:
        inf = max(self.first_bin, bin_range.inf)
        sup = min(self.last_bin, bin_range.sup)
        return Interval(self.bin_lower_edge(inf),
                        self.bin_upper_edge(sup))

   ###############################################

    def sub_binning(self, interval: Interval) -> 'Binning1D':
        return self.__class__(interval, self._bin_width)

####################################################################################################

class NDMixin:

    ##############################################

    def __init__(self, *objs) -> None:
        self._objs = list(objs)

    ##############################################

    @property
    def x(self) -> Binning1D:
        return self._objs[0]

    @property
    def y(self) -> Binning1D:
        return self._objs[1]

    @property
    def dimension(self) -> int:
        return len(self._objs)

    ##############################################

    def __len__(self) -> int:
        return len(self._objs)

    def __iter__(self) -> Iterator[Binning1D]:
        return iter(self._objs)

    def __getitem__(self, i) -> Binning1D:
        return self._objs[i]

####################################################################################################

class BinningND(NDMixin):

    ##############################################

    def find_bin(self, *args) -> tuple[int]:
        # Numpy index must be a tuple
        return tuple([binning.find_bin(x) for binning, x in zip(self, args)])

    ##############################################

    def bin_slice(self, xflow=False):
        return [binning.bin_slice(xflow) for binning in self]

    ##############################################

    @property
    def bin_centers(self):
        return [binning.bin_centers for binning in self]
