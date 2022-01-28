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

from enum import Enum
from pathlib import Path
from pprint import pprint
import logging

import matplotlib.pyplot as plt

from SnowAvalancheData.Data import AccidentRegister, Accident
from SnowAvalancheData.Data.DataType import *
from SnowAvalancheData.Plot import Figure
from SnowAvalancheData.Statistics.Histogram import Histogram, EnumHistogram, Binning1D, Interval

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Analysis:

    _logger = _module_logger.getChild('Analysis')

    ATTRIBUTE_BIN_WIDTH = {
        'altitude': 250,   # m
        'height_difference': 100,   # m
        'length': 100,   # m
        'rescue_delay': 20,   # min
        'thickness_max': 20,   # cm
        'width': 15,   # m
    }

    ATTRIBUTE_TITLE = {
        'orientation': 'Slope Orientation',
        'move_direction': 'Moving Direction',
    }

    ATTRIBUTE_MAPPER = {
        'rescue_delay': 'rescue_delay_minutes',
    }

    ##############################################

    @classmethod
    def relative_to_source(cls, *args):
        return Path(__file__).parents[2].joinpath(*args)

    ##############################################

    def __init__(self, path: Path) -> None:
        self.accidents = None
        self.load_data(path)
        self.filter_data()
        self.create_histograms()
        self.fill_histograms()
        self.post_process_histograms()
        # self.plot()

    ##############################################

    def load_data(self, path: Path) -> None:
        self._logger.info(f'Load {path}')
        self.accidents = AccidentRegister.load_json(path)

    ##############################################

    def filter_data(self) -> None:
        self.filtered_accidents = self.accidents.and_filter(
            activity=lambda _: _ in (Activity.HIKING, Activity.MOUNTAINEERING),
        )

    ##############################################

    def create_histograms(self) -> None:
        self._logger.info('Create histograms')
        self.histograms = {}
        for attribute, type_ in Accident.attribute_types():
            title = self.ATTRIBUTE_TITLE.get(attribute, attribute.replace('_', ' '))
            unit = Accident.ATTRIBUTE_UNIT.get(attribute, '')
            if issubclass(type_, Enum):
                self.histograms[attribute] = EnumHistogram(type_, title=title, unit=unit)
            elif type_ in (int, float, Delay):
                self._logger.info(f'  Scan inf/sup for {attribute}')
                _ = self.ATTRIBUTE_MAPPER.get(attribute, attribute)
                inf, sup = self.filtered_accidents.inf_sup(_)
                sup += 1
                bin_width = self.ATTRIBUTE_BIN_WIDTH.get(attribute, 1)
                self._logger.info(f'{attribute} [{inf}, {sup}] bw = {bin_width}')
                self.histograms[attribute] = Histogram(binning=Binning1D(Interval(inf, sup), bin_width=bin_width), title=title, unit=unit)

        self.ratio_histograms = {}
        for attribute in Accident.RATIO_ATTRIBUTES:
            histogram = self.histograms[attribute]
            title = f'ratio {histogram.title}'
            unit = 'percent'
            inf = 0
            sup = 100
            bin_width = 10
            self.ratio_histograms[attribute] = Histogram(binning=Binning1D(Interval(inf, sup), bin_width=bin_width), title=title, unit=unit)

    ##############################################

    def fill_histograms(self) -> None:
        self._logger.info('Fill histograms')
        # Fixme: also impl vectorize / vs cpu ram
        for accident in self.filtered_accidents:
            # pself._logger.info(accident.__dict__)
            for attribute, histogram in self.histograms.items():
                _ = self.ATTRIBUTE_MAPPER.get(attribute, attribute)
                value = getattr(accident, _)
                if value is not None:
                    histogram.fill(value)
                    if attribute in Accident.RATIO_ATTRIBUTES:
                        value = getattr(accident, f'ratio_{attribute}')
                        if value is not None:
                            ratio_histogram = self.ratio_histograms[attribute]
                            ratio_histogram.fill(value)

    ##############################################

    def post_process_histograms(self) -> None:
        for attribute, histogram in self.histograms.items():
            histogram.normalise(to_percent=True, clone=False)

    ##############################################

    def dumo_histograms(self) -> None:
        for attribute, histogram in self.histograms.items():
                self._logger.info("="*100)
                self._logger.info(attribute)
                self._logger.info(histogram)

    ##############################################

    def plot(self) -> None:
        self._logger.info('Plot...')

        # plt.rcParams["figure.figsize"]=15,8

        def plot_histogram(figure, attribute):
            histogram = self.histograms[attribute]
            match attribute:
                case 'bra_level' | 'departement':
                    figure.bar_number(histogram)
                case 'orientation':
                    figure.polar_bar(histogram)
                case _:
                    match histogram:
                       case EnumHistogram():
                           figure.bar(histogram)
                       case Histogram():
                           figure.histogram(histogram)

        with Figure('figure1', number_of_rows=2, number_of_columns=3) as figure:
            for attribute in (
                    'activity',
                    'altitude',
                    'departement',   # -> map
                    # 'date',
                    'gear',
            ):
                plot_histogram(figure, attribute)

        with Figure('figure2', number_of_rows=2, number_of_columns=4) as figure:
            for attribute in (
                    'bra_level',
                    'move_direction',
                    'orientation',
                    'snow_cohesion',
                    #
                    'snow_quality',
                    'start_reason',
                    'start_type',
                    # 'inclination',
        ):
                plot_histogram(figure, attribute)

        with Figure('figure3', number_of_rows=2, number_of_columns=2) as figure:
            for attribute in (
                    'length',
                    'width',
                    #
                    'height_difference',
                    'thickness_max',
            ):
                plot_histogram(figure, attribute)

        with Figure('figure', number_of_rows=3, number_of_columns=4) as figure:
            for attribute in (
                    'number_of_persons',
                    'safe',
                    'injured',
                    'dead',
                    #
                    'carried_away',
                    'partial_bluried_non_critical',
                    'partial_bluried_critical',
                    #
                    'head_bluried',
                    'full_bluried',
            ):
                plot_histogram(figure, attribute)

        with Figure('figure5', number_of_rows=3, number_of_columns=4) as figure:
            for attribute in (
                    'safe',
                    'injured',
                    'dead',
                    #
                    'carried_away',
                    'partial_bluried_non_critical',
                    'partial_bluried_critical',
                    #
                    'head_bluried',
                    'full_bluried',
            ):
                # plot_histogram(figure, f'ratio_{attribute}')
                figure.histogram(self.ratio_histograms[attribute])

        with Figure('figure6', number_of_rows=2, number_of_columns=2) as figure:
            for attribute in (
                    'alert_device',
                    'alert_person',
                    #
                    'rescue_delay',
                    # 'doctor_on_site',
            ):
                plot_histogram(figure, attribute)

    ##############################################

    def save_figures(self) -> None:
        figures = {key: value for key, value in globals().items() if isinstance(value, Figure)}
        for name, figure in figures.items():
            figure.save(f'{name}.svg')