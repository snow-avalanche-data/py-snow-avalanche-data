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

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from SnowAvalancheData.Statistics.Histogram import EnumHistogram, Histogram

####################################################################################################

class Figure:

    ##############################################

    def __init__(self, number_of_rows: int, number_of_columns: int) -> None:
        # figsize=(5, 2.7), layout='constrained'
        self._number_of_columns = number_of_columns
        self._figure, self._axes = plt.subplots(number_of_rows, number_of_columns)
        self._location = 0

    ##############################################

    def next_location(self) -> tuple[int, int]:
        r = int(self._location // self._number_of_columns)
        c = int(self._location % self._number_of_columns)
        self._location += 1
        return r, c

    ##############################################

    def _get_axe(self, axe: list=None):
        r, c = axe or self.next_location()
        return self._axes[r][c]

    ##############################################

    def plot_bar(self, histogram: EnumHistogram, title: str, axe: list=None) -> None:
        ax = self._get_axe(axe)
        indexes, y, y_errors = histogram.to_graph()
        ax.bar(indexes, y, width=.3, yerr=y_errors, label=title)
        ax.set_title(title)
        ax.set_xticks(indexes, labels=histogram.labels)
        ax.grid(True)

    ##############################################

    def plot_histogram(self, histogram: Histogram, title: str, axe: list=None) -> None:
        ax = self._get_axe(axe)
        x, y, x_errors, y_errors = histogram.to_graph()
        ax.errorbar(x, y, y_errors, fmt='o', linewidth=2, capsize=6)
        ax.set_title(title)
        # ax.set_xticks(indexes, labels=histogram.labels)
        ax.grid(True)

    ##############################################

    def plot_bar_number(self, histogram: Histogram, title: str, axe: list=None) -> None:
        ax = self._get_axe(axe)
        x, y, x_errors, y_errors = histogram.to_graph(centred=False)
        ax.bar(x, y, width=.3, yerr=y_errors, label=title)
        ax.set_title(title)
        ax.grid(True)

