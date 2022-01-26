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
    'BinningND',
    'EnumHistogram',
    'Histogram',
    'Histogram2D',
    'Interval',
]

####################################################################################################

from enum import Enum, auto
import math

import numpy as np

from .Binning import Binning1D, BinningND, Interval, NDMixin

####################################################################################################

class DataSetMoment:

    ##############################################

    def __init__(
            self,
            number_of_entries: int=0,
            sum_x: float=0, sum_x2: float=0, sum_x3: float=0, sum_x4: float=0,
    ) -> None:
        self.number_of_entries = number_of_entries
        self.sum_x = sum_x
        self.sum_x2 = sum_x2
        self.sum_x3 = sum_x3
        self.sum_x4 = sum_x4 # unused

    ##############################################

    def clone(self) -> 'DataSetMoment':
        return self.__class__(
            self.number_of_entries,
            self.sum_x, self.sum_x2, self.sum_x3, self.sum_x4,
        )

    ##############################################

    def to_json(self) -> dict:
        return {
            'number_of_entries': self.number_of_entries,
            'sum_x': self.sum_x,
            'sum_x2': self.sum_x2,
            'sum_x3': self.sum_x3,
            'sum_x4': self.sum_x4,
        }

    ##############################################

    @classmethod
    def from_json(cls, data) -> 'DataSetMoment':
        return cls(**data)

    ##############################################

    def fill(self, x: float) -> None:
        self.number_of_entries += 1
        self.sum_x += x
        self.sum_x2 += x**2
        self.sum_x3 += x**3
        self.sum_x4 += x**4

    ##############################################

    def __iadd__(self, obj: 'DataSetMoment') -> 'DataSetMoment':
        self.number_of_entries += obj.number_of_entries
        self.sum_x += obj.sum_x
        self.sum_x2 += obj.sum_x2
        self.sum_x3 += obj.sum_x3
        self.sum_x4 += obj.sum_x4
        return self

    ##############################################

    @property
    def mean(self) -> float:
        return self.sum_x / self.number_of_entries

    @property
    def biased_variance(self) -> float:
        return self.sum_x2 / self.number_of_entries - self.mean**2

    @property
    def unbiased_variance(self) -> float:
        return self.number_of_entries / (self.number_of_entries -1) * self.biased_variance

    @property
    def biased_standard_deviation(self) -> float:
        return math.sqrt(self.biased_variance)

    @property
    def standard_deviation(self) -> float:
        return math.sqrt(self.unbiased_variance)

    @property
    def skew(self) -> float:
        return ((self.sum_x3 / self.number_of_entries - 3*self.mean*self.biased_variance - self.mean**3)
                / (self.biased_variance*self.biased_standard_deviation))

    @property
    def kurtosis(self) -> float:
        # Need an expansion in terms of sum_x**i
        return NotImplementedError

####################################################################################################

class DataSetMomentND(NDMixin):

    ##############################################

    def __init__(self, dimension: int) -> None:
        NDMixin.__init__(self, [DataSetMoment() for i in range(dimension)])

    ##############################################

    def fill(self, *args) -> None:
        pass
        # Fixme:
        # for data_set_moment, x in zip(self, args):
        #     data_set_moment.fill(x)

####################################################################################################

class WeightedDataSetMoment:

    ##############################################

    def __init__(self) -> None:
        self.sum_weight = 0
        self.sum_weight2 = 0
        self.sum_weight_x = 0
        self.sum_weight_x2 = 0
        self.sum_weight_x3 = 0
        self.sum_weight_x4 = 0

    ##############################################

    def fill(self, x: float, weight: float=1.) -> None:
        self.sum_weight += weight
        self.sum_weight2 += weight**2
        weight_x = weight * x
        self.sum_weight_x += weight_x
        self.sum_weight_x2 += weight_x**2
        self.sum_weight_x3 += weight_x**3
        self.sum_weight_x4 += weight_x**4

    ##############################################

    @property
    def number_of_effective_entries(self) -> float:
        return self.sum_weight**2 / self.sum_weight2

    @property
    def mean(self) -> float:
        return self.sum_weight_x / self.number_of_effective_entries

####################################################################################################

class UnitType(Enum):
    COUNT = auto()
    NORMALISED = auto()
    PERCENT = auto()

####################################################################################################

class Histogram:

    ##############################################

    def __init__(self, binning: Binning1D, **kwargs) -> None:
        if isinstance(binning, Binning1D):
            self._binning = binning
        else:
            raise ValueError
        self._title = str(kwargs.get('title', ''))
        self._unit = str(kwargs.get('unit', ''))
        self._y_unit = UnitType.COUNT
        self._make_array(self._binning.array_size)
        self.data_set_moment = DataSetMoment()
        self.clear_feature()

    ##############################################

    def _make_array(self, array_size: int) -> None:
        self._accumulator = np.zeros(array_size)
        self._sum_weight_square = np.zeros(array_size)

    ##############################################

    def clone(self) -> 'Histogram':
        # , title=self._title, unit=self._unit
        histogram = self.__class__(self._binning.clone())
        histogram += self
        for _ in ('_title', '_unit', '_y_unit'):
            setattr(histogram, getattr(self, _))
        return histogram

    ##############################################

    def to_json(self) -> dict:
        return {
            'title': self._title,
            'binning': self._binning.to_json(),
            'data_set_moment': self.data_set_moment.to_json(),
            'accumulator': list(self._accumulator),
            'sum_weight_square': list(self._sum_weight_square),
        }

    ##############################################

    @classmethod
    def from_json(cls, data: dict) -> 'Histogram':
        binning = cls.from_json(data['binning'])
        histogram = Histogram(binning, title=data['title'])
        histogram.data_set_moment += DataSetMoment.from_json(data['data_set_moment'])
        histogram._accumulator[...] = data['accumulator']
        histogram._sum_weight_square[...] = data['sum_weight_square']
        return histogram

    ##############################################

    def clear(self, value: float=.0) -> None:
        self._accumulator[:] = value
        self._sum_weight_square[:] = value**2
        self.data_set_moment = DataSetMoment()
        self.clear_feature()

    ##############################################

    def clear_feature(self) -> None:
        self._errors = None
        self._integral = None
        self._mean = None
        self._biased_variance = None

    ##############################################

    def rebin(self, factor: int=2) -> 'Histogram':
        histogram = self.__class__(Binning1D(self._binning.interval, bin_width=self._binning.bin_width*factor))
        binning = histogram.binning

        # copy under/over flow bins
        for i in (0, -1):
            histogram._accumulator[i] = self._accumulator[i]
            histogram._sum_weight_square[i] = self._sum_weight_square[i]

        start = 1
        for i in binning.bin_iterator():
            stop = min(start + factor, self.binning.number_of_bins)
            histogram._accumulator[i] = np.sum(self._accumulator[start:stop])
            histogram._sum_weight_square[i] = np.sum(self._sum_weight_square[start:stop])
            start = stop

        # Fixme: merge last bin when the rebin factor is not a multiple
        over_flow_bin = self.binning.over_flow_bin
        if stop < over_flow_bin:
            histogram._accumulator[i] += np.sum(self._accumulator[stop:over_flow_bin])
            histogram._sum_weight_square[i] += np.sum(self._sum_weight_square[stop:over_flow_bin])

        histogram.data_set_moment += self.data_set_moment

        return histogram

    ##############################################

    def bin_label(self, i: int):
        return ''

    ##############################################

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        self._title = str(value)

    @property
    def unit(self) -> str:
        return self._unit

    @property
    def y_unit(self) -> UnitType:
        return self._y_unit

    @property
    def binning(self) -> Binning1D:
        return self._binning

    @property
    def accumulator(self) -> np.ndarray:
        return self._accumulator

    @property
    def binning_accumulator(self) -> np.ndarray:
        return self._accumulator[1:-1]

    @property
    def underflow_accumulator(self) -> float:
        return self._accumulator[0]

    @property
    def overflow_accumulator(self) -> float:
        return self._accumulator[-1]

    @property
    def has_overflow(self) -> bool:
        return self.underflow_accumulator != 0 or self.overflow_accumulator != 0

    @property
    def x_values(self) -> np.ndarray:
        return self._binning.bin_centers

    @property
    def min(self) -> float:
        # return min(self._accumulator) # - self._errors
        return float(np.min(self._accumulator))

    @property
    def max(self) -> float:
        # return max(self._accumulator) # + self._errors
        return float(np.max(self._accumulator))

    inf = min
    sup = max

    ##############################################

    def is_consistent_with(self, obj: 'Histogram') -> bool:
        return self._binning == obj._binning

    ##############################################

    # | float
    def __iadd__(self, obj: 'Histogram') -> 'Histogram':
        """Add an histogram"""
        if isinstance(obj, Histogram):
            if self.is_consistent_with(obj):
                self._accumulator += obj._accumulator
                self._sum_weight_square += obj._sum_weight_square
                self.data_set_moment += obj.data_set_moment
            else:
                raise ValueError
        else:
            float_obj = float(obj)
            self._accumulator += float_obj
            self._sum_weight_square += float_obj**2
            # self.data_set_moment += ...
        self.clear_feature()
        return self

    ##############################################

    def __isub__(self, obj: 'Histogram') -> 'Histogram':
        if isinstance(obj, Histogram):
            if self.is_consistent_with(obj):
                self._accumulator -= obj._accumulator
                self._sum_weight_square -= obj._sum_weight_square
                self.data_set_moment -= obj.data_set_moment
            else:
                raise ValueError
        else:
            float_obj = float(obj)
            self._accumulator -= float_obj
            self._sum_weight_square -= float_obj**2
            # self.data_set_moment -= ...
        self.clear_feature()
        return self

    ##############################################

    def __imul__(self, obj: 'Histogram') -> 'Histogram':
        # Fixme: data_set_moment
        if isinstance(obj, Histogram):
            if self.is_consistent_with(obj):
                self._accumulator *= obj._accumulator
                self._sum_weight_square[...] = 0
                # self._sum_weight_square *= obj._sum_weight_square
                # self.data_set_moment *= obj.data_set_moment # Fixme: Right ???
            else:
                raise ValueError
        else:
            obj = float(obj)
            self._accumulator *= obj
            self._sum_weight_square *= obj**2
            # self.data_set_moment *= obj
        self.clear_feature()
        return self

    ##############################################

    def __itruediv__(self, obj: 'Histogram') -> 'Histogram':
        # Fixme: data_set_moment
        if isinstance(obj, Histogram):
            if self.is_consistent_with(obj):
                numerator = self._accumulator
                denominator = obj._accumulator
                efficiency = np.nan_to_num(numerator / denominator)
                self._accumulator = efficiency
                self._sum_weight_square[...] = self._binomial_variance_unweighted(efficiency, denominator)
                # self.data_set_moment /= obj.data_set_moment # Fixme: Right ???
            else:
                raise ValueError
        else:
            float_obj = float(obj)
            self._accumulator /= float_obj
            self._sum_weight_square /= float_obj**2
            # self.data_set_moment /= float_obj
        self.clear_feature()
        return self

    ##############################################

    def __add__(obj1, obj2: 'Histogram') -> 'Histogram':
        obj = obj1.clone()
        obj += obj2
        return obj

    ##############################################

    def __sub__(obj1, obj2: 'Histogram') -> 'Histogram':
        obj = obj1.clone()
        obj -= obj2
        return obj

    ##############################################

    def __mul__(obj1, obj2: 'Histogram') -> 'Histogram':
        obj = obj1.clone()
        obj *= obj2
        return obj

    ##############################################

    def __truediv__(obj1, obj2: 'Histogram') -> 'Histogram':
        obj = obj1.clone()
        obj /= obj2
        return obj

    ##############################################

    def fill(self, *values: list[float], weight: float=1.) -> None:
        if weight < 0:
            raise ValueError
        i = self._binning.find_bin(*values)
        self._accumulator[i] += weight
        # if weight == 1.: weight_square = 1.
        self._sum_weight_square[i] += weight**2
        self.data_set_moment.fill(*values)
        self.clear_feature()

    ##############################################

    def compute_errors(self) -> None:
        if self._errors is None:
            self._errors = np.sqrt(self._sum_weight_square)

    ##############################################

    def get_bin_error(self, i: int) -> float:
        self.compute_errors()
        return self._errors[i]

    ##############################################

    @property
    def integral(self) -> float:
        """Compute histogram integral.

        Warning: overflow bin are summed.

        """
        if self._integral is None:
            self._integral = self._accumulator.sum()
        return self._integral

    ##############################################

    @property
    def number_of_effective_entries(self) -> float:
        return self.integral**2 / self._sum_weight_square.sum()

    ##############################################

    @property
    def mean(self) -> float:
        if self._mean is None:
            # if weighted: / self.number_of_effective_entries
            self._mean = np.sum(self.binning_accumulator * self.x_values) / self.integral
        return self._mean

    ##############################################

    @property
    def biased_variance(self) -> float:
        if self._biased_variance is None:
            self._biased_variance = np.sum(self.binning_accumulator * self.x_values**2) / self.integral - self.mean**2
        return self._biased_variance

    ##############################################

    @property
    def unbiased_variance(self) -> float:
        return self.integral / (self.integral -1) * self.biased_variance

    ##############################################

    @property
    def biased_standard_deviation(self) -> float:
        return math.sqrt(self.biased_variance)

    ##############################################

    @property
    def standard_deviation(self) -> float:
        return math.sqrt(self.unbiased_variance)

    ##############################################

    @property
    def skew(self) -> float:
        # self.biased_variance * self.biased_standard_deviation
        return (np.sum(self.binning_accumulator * (self.x_values - self.mean)**3)
                / (self.biased_standard_deviation**3 * self.integral))

    ##############################################

    @property
    def kurtosis(self) -> float:
        return (np.sum(self.binning_accumulator * (self.x_values - self.mean)**4)
                / (self.biased_variance**2 * self.integral)
                -3)

    ##############################################

    def _clone(self, clone=True) -> 'Histogram':
        if clone:
            return self.clone()
        else:
            return self

    ##############################################

    def normalise(self, scale: float=1, clone: bool=True, to_percent: bool=False) -> 'Histogram':
        if to_percent:
            scale = 100
        match scale:
            case 1:
                self._y_unit = UnitType.NORMALISED
            case 100:
                self._y_unit = UnitType.PERCENT
        histogram = self._clone(clone)
        histogram *= scale / histogram.integral
        histogram.clear_feature()
        return histogram

    ##############################################

    def cumulative(self, normalise: bool=True, clone=True) -> 'Histogram':
        if self.has_overflow:
            raise NotImplementedError
        histogram = self._clone(clone)
        histogram.clear_feature()
        histogram._accumulator = np.cumsum(histogram._accumulator)
        histogram._accumulator[-1] = 0   # clear cumsum on overflow bin
        histogram._sum_weight_square = np.cumsum(histogram._sum_weight_square)
        if normalise:
            histogram *= 100 / histogram._accumulator[-2]
            histogram._y_unit = UnitType.PERCENT
        histogram.title = f'{self.title} cumulative'
        return histogram

    ##############################################

    def inverse_cumulative(self, normalise: bool=True, clone=True) -> 'Histogram':
        histogram = self._clone(clone)
        denominator = histogram.integral
        if normalise:
            histogram._accumulator /= denominator
            sup = 1
        else:
            sup = histogram.integral
        inverse_cumulative = sup - np.cumsum(histogram._accumulator)   # overflow ?
        histogram._accumulator[1] = sup
        histogram._accumulator[2:-1] = inverse_cumulative[1:-2]
        # Fixme: check, should be computed in div
        histogram._sum_weight_square[...] = self._binomial_variance_unweighted(histogram._accumulator, denominator)
        histogram.clear_feature()
        return histogram

    ##############################################

    def efficiency(self):
        # eff = Sum x>t / integral
        return self.inverse_cumulative()

    ##############################################

    def purity(self, denominator):
        # eff = Sum N x>t / Sum D x>t
        numerator = self.inverse_cumulative(normalise=False)
        denominator = denominator.inverse_cumulative(normalise=False)
        purity = numerator / denominator
        return purity

   ###############################################

    def find_non_zero_bin_range(self) -> Interval:
        inf = 0
        while self._accumulator[inf] == 0:
            inf += 1
        sup = len(self._accumulator) -1
        while self._accumulator[sup] == 0:
            sup -= 1
        return Interval(inf, sup)

   ###############################################

    def non_zero_bin_range_histogram(self) -> 'Histogram':
        bin_range = self.find_non_zero_bin_range()
        binning = self._binning.sub_binning(self._binning.sub_interval(bin_range))
        histogram = self.__class__(binning)
        src_slice = slice(bin_range.inf, bin_range.sup +1)
        dst_slice = slice(binning.first_bin, binning.over_flow_bin)
        histogram._accumulator[dst_slice] = self._accumulator[src_slice]
        histogram._sum_weight_square[dst_slice] = self._sum_weight_square[src_slice]
        histogram._errors[dst_slice] = self._errors[src_slice]
        return histogram

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

        if not non_null:
            edges = np.zeros(len(y) +1)
            edges[:-1] = binning.bin_lower_edges()
            edges[-1] = binning.interval.sup
            return x, y, x_errors, y_errors, edges
        else:
            return x, y, x_errors, y_errors

   ###############################################

    def __str__(self):
        binning = self._binning
        text = f"""
Histogram 1D: {self._title}
  unit: {self._unit}
  y_unit: {self._y_unit}
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

    def __init__(self, cls, **kwargs) -> None:
        # Fixme: private API
        self._cls = cls
        self._map = cls._value2member_map_
        self._labels = [str(_).split('.')[1] for _ in cls]
        values = self._map.keys()
        inf = min(values)
        sup = max(values) +1
        binning = Binning1D(Interval(inf, sup), bin_width=1)
        super().__init__(binning, **kwargs)

    ##############################################

    def clone(self) -> 'EnumHistogram':
        # Fixme:
        #  histogram = super().clone()
        histogram = self.__class__(self._cls)
        histogram += self
        for _ in ('_title', '_unit', '_y_unit'):
            setattr(histogram, _, getattr(self, _))
        return histogram

    ##############################################

    def to_json(self) -> dict:
        raise NotImplementedError

    ##############################################

    @classmethod
    def from_json(cls, data: dict) -> 'EnumHistogram':
        raise NotImplementedError

    ##############################################

    @property
    def labels(self) -> list[str]:
        return self._labels

    ##############################################

    def fill(self, x, weight: float=1.) -> None:
        if x is not None:
            super().fill(x.value, weight=weight)

    ##############################################

    def bin_label(self, i: int) -> str:
        try:
            return self._map[i]
        except KeyError:
            return ''

    ##############################################

    def to_graph(self, non_null=True):
        # Fixme: duplicated code
        self.compute_errors()

        binning = self._binning
        bin_slice = binning.bin_slice()

        y = np.copy(self._accumulator[bin_slice])
        y_errors = np.copy(self._errors[bin_slice])

        x = np.arange(binning.number_of_bins)

        if non_null:
            indices = np.where(y != 0)
            x = x[indices]
            y = y[indices]
            y_errors = y_errors[indices]

        return x, y, y_errors

####################################################################################################

class Histogram2D(Histogram):

    ##############################################

    def __init__(self, binning: BinningND) -> None:
        if isinstance(binning, BinningND) and binning.dimension == 2:
            self._binning = binning
        else:
            raise ValueError

        array_size = [binning.array_size for binning in self._binning]
        self._make_array(array_size)
        self.data_set_moment = DataSetMomentND(dimension=2)

        # self.clear_feature()
