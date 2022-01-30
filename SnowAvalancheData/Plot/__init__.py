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

from pathlib import Path
from typing import Optional

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from SnowAvalancheData.Statistics.Histogram import EnumHistogram, Histogram, Histogram2D, UnitType

####################################################################################################

class Figure:

    A4 = (297, 210)
    A5 = (A4[1], A4[0]//2)   # 148

    Y_UNIT_MAP = {
        UnitType.COUNT: '#',
        UnitType.NORMALISED: '%',
        UnitType.PERCENT: '%',
    }

    POOL = {}

    ##############################################

    @classmethod
    def mm2in(cls, x: float) -> float:
        return x / 25.4

    ##############################################

    def __init__(self,
                 name: str,
                 number_of_rows: int,
                 number_of_columns: int,
                 figure_size: Optional[tuple[float, float]]=None,
                 ) -> None:

        self._name = str(name)
        self.POOL[self._name] = self

        if figure_size is None:
            figure_size = [self.mm2in(_) for _ in self.A5]

        # https://matplotlib.org/stable/tutorials/intermediate/constrainedlayout_guide.html
        # https://matplotlib.org/stable/tutorials/intermediate/tight_layout_guide.html
        self._figure, self._axes = plt.subplots(
            number_of_rows, number_of_columns,
            dpi=100,
            figsize=figure_size,
            constrained_layout=True,
            # projection='polar',
            # layout='constrained',
            # constrained_layout_pads=0.1,
        )
        # self._figure.tight_layout(pad=3.0, w_pad=3.0, h_pad=3.0)

        self._number_of_rows = number_of_rows
        self._number_of_columns = number_of_columns
        self._location = -1
        for _ in self._axes.flat:
            _.set_visible(False)

    ##############################################

    # def __del__(self):
    #     pass

    ##############################################

    def __enter__(self):
        return self

    ##############################################

    def __exit__(self, exc_type, exc_value, exc_tb):
        pass

    ##############################################

    def next_location(self) -> int:
        self._location += 1
        return self._location

    ##############################################

    def _get_axe(self, axe: list=None) -> mpl.axes:
        _ = self._axes.flat[self.next_location()]
        _.set_visible(True)
        return _

    ##############################################

    def _r_c(self) -> tuple[int, int]:
        return int(self._location // self._number_of_columns), int(self._location % self._number_of_columns)

    ##############################################

    def bar(self, histogram: EnumHistogram, title: str=None, axe: list=None) -> None:
        ax = self._get_axe(axe)

        ax.set_title(title or histogram.title)
        ax.set_ylabel(self.Y_UNIT_MAP[histogram.y_unit])
        ax.grid(True)

        indexes, y, y_errors = histogram.to_graph()

        # print('---')
        # print(indexes, histogram.labels)

        labels = []
        has_long_label = False
        for i, label in enumerate(histogram.labels):
            if i not in indexes:
                continue
            if len(label) > 5:
                label = label[:5]
                has_long_label = True
            labels.append(label)

        indexes = np.arange(0, len(indexes))
        # print(indexes, labels)

        ax.bar(indexes, y, width=.3, yerr=y_errors)   # , label=title
        ax.set_xticks(indexes, labels=labels)
        if has_long_label:
            # Fixme: -> func
            for tick in ax.get_xticklabels():
                tick.set_rotation(45)

    ##############################################

    def histogram(self, histogram: Histogram, title: str=None, axe: list=None) -> None:
        ax = self._get_axe(axe)

        ax.set_title(title or histogram.title)
        ax.set_xlabel(histogram.unit)
        ax.set_ylabel(self.Y_UNIT_MAP[histogram.y_unit])
        ax.grid(True)

        x, y, x_errors, y_errors, edges = histogram.to_graph(non_null=False)
        ax.stairs(y, edges, fill=True)
        x, y, x_errors, y_errors = histogram.to_graph()
        ax.errorbar(x, y, y_errors, fmt='o', linewidth=2, capsize=6)

        binning = histogram.binning
        # x_ticks = np.arange(binning.interval.inf, binning.interval.sup, binning.bin_width)
        offset = binning.bin_width / 2
        inf = x[0]-offset
        sup = x[-1]+3*offset
        x_ticks = binning.bins()   # np.arange(inf, sup, step=binning.bin_width)
        ax.set_xticks(x_ticks)
        # Fixme: inf!
        # ax.set_xlim(0, sup)
        ax.set_xlim(inf, sup)
        if len(x_ticks) > 10:
            for tick in ax.get_xticklabels():
                tick.set_rotation(90)
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.tick_params.html
        # ax.tick_params(axis='x', Labelsize=)

    ##############################################

    def bar_number(self, histogram: Histogram, title: str=None, axe: list=None) -> None:
        ax = self._get_axe(axe)
        ax.set_title(title or histogram.title)
        ax.set_ylabel(self.Y_UNIT_MAP[histogram.y_unit])
        ax.grid(True)

        x, y, x_errors, y_errors = histogram.to_graph(centred=False)
        labels = [str(int(_)) for _ in x]
        indexes = np.arange(0, len(x))

        ax.bar(indexes, y, yerr=y_errors, width=.3)
        ax.set_xticks(indexes, labels=labels)

    ##############################################

    def polar_bar(self, histogram: Histogram, title: str=None, axe: list=None) -> None:
        ax = self._get_axe(axe)
        ax.remove()
        ax = self._figure.add_subplot(self._number_of_rows, self._number_of_columns, self._location +1, projection='polar')

        ax.set_title(title or histogram.title)
        ax.grid(True)

        indexes, y, y_errors = histogram.to_graph()
        # theta = np.linspace(0, 2*np.pi, 8, endpoint=False)
        theta = np.array([90, 45, 0, 315, 271, 225, 181, 135]) * 2*np.pi / 360
        ax.bar(theta, y, yerr=y_errors, width=(np.pi/4 * .90), color='tab:blue', alpha=.8)
        # ax.bar(theta, y + y_errors, width=(np.pi/4 * .90), color='tab:blue', alpha=.8)
        # ax.bar(theta, y, width=(np.pi/4 * .90), color='tab:blue', alpha=1.0)
        # ax.bar(theta, y - y_errors, width=(np.pi/4 * .90), color='white', alpha=.8)
        ax.set_xticks(theta, labels=histogram.labels)

    ##############################################

    def box_plot(self, histogram: Histogram2D, title: str, axe: list=None) -> None:
        """Also called Hinton diagram"""
        ax = self._get_axe(axe)

        ax.set_title(title or histogram.title)
        ax.set_xlabel(histogram.x_label)
        ax.set_ylabel(histogram.y_label)

        if np.min(histogram.accumulator) < 0:
            raise ValueError("Bin contents must be positive")

        # Set bin content to a normalised square area
        accumulator_view = histogram.accumulator[1:-1,1:-1]
        accumulator = np.sqrt(accumulator_view / np.max(accumulator_view))
        # Add margin
        accumulator *= .90

        for (x, y), size in np.ndenumerate(accumulator):
            rectangle = plt.Rectangle([x - size / 2, y - size / 2], size, size,
                                      edgecolor='black', facecolor='white')
            ax.add_patch(rectangle)

        ax.set_aspect('equal', 'box')
        x_size, y_size = accumulator_view.shape
        ax.set_xlim(-.5, x_size)
        ax.set_ylim(-.5, y_size)
        labels = [f'{_:g}' for _ in histogram.binning.x.bins()]
        ax.set_xticks(np.arange(x_size +1) -.5, labels, rotation='vertical')
        labels = [f'{_:g}' for _ in histogram.binning.y.bins()]
        ax.set_yticks(np.arange(y_size +1) -.5, labels)

    ##############################################

    def save(self, path: Path) -> None:
        print(f'Save {path}')
        self._figure.savefig(path)
