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

"""Module to convert Anena XLS data files to the JSON format.

In details, this code convert a sheet row in a JSON dictionary.  It also performs some fixes on the
cell values and translate the enumerate from French to English.

"""

####################################################################################################

__all__ = [
    'AccidentBook',
    'Accident',
    'AccidentRegister',
]

####################################################################################################

from enum import Enum
from pathlib import Path
from typing import Iterator
import datetime
import json
import logging
import os
import re

# import csv
# import pandas as pd   # requires xlrd
import xlrd

from SnowAvalancheData.Data import Accident as DataAccident
from SnowAvalancheData.Data import AccidentRegister, DataType
from SnowAvalancheData.Data.DataType import Delay, Inclination
from SnowAvalancheData.Cartography.Projection import Utm
from SnowAvalancheData.Cartography.Ign import IgnApi

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

IGN_API = None

####################################################################################################

FRENCH_TRANSLATION = {
    'français': 'fr',
    'féminin': 'female',
    'masculin': 'male',
    # 'non': False,
    # 'oui': True,
}

def translate_from_fr(string: str) -> str:
    return FRENCH_TRANSLATION.get(string, string)

####################################################################################################

def fr_to_bool(value: str) -> bool:
    match value:
       case 'non':
           return False
       case 'oui':
           return True
    raise ValueError(value)

####################################################################################################

class MappedEnum:
    _subclasses = []
    _map = {}

    ##############################################

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls._subclasses.append(cls)
        cls._init_map()

    ##############################################

    @classmethod
    def _init_map(cls) -> None:
        map_ = cls.MAP
        for key, value in map_.items():
            map_[key] = getattr(cls.CLS, value)
        cls._map[cls] = map_

    ##############################################

    @classmethod
    def translate(cls, value: str):
        return cls._map[cls][value]

    ##############################################

    @classmethod
    def to_json(cls, value) -> str:
        _ = str(value).lower()
        return _.split('.')[1]

####################################################################################################

class Activity(MappedEnum):
    CLS = DataType.Activity

    MAP = {
        'accès refuge gardien ski rando': 'HUT_ACCESS',
        'alpinisme': 'MOUNTAINEERING',
        'autre': 'OTHER',
        'entrainement militaire descente couloir': 'MILITARY',
        'equipement piste': 'SKI_SLOPE_MAINTENANCE',
        'habitation': 'HOME',
        'hors-piste': 'OFF_ROAD',
        'minage': 'MINING',
        'piste': 'SKI_SLOPE',
        'randonnée': 'HIKING',
        'relevés EDF / déplacement ski de rando': 'EDF',
        'voie de communication': 'ROAD',
    }

####################################################################################################

class Gear(MappedEnum):
    CLS = DataType.Gear

    MAP = {
        'à pieds': 'ON_FOOT',
        'raquettes': 'SNOWSHOE',
        'ski fond': 'CROSS_COUNTRY_SKIING',
        'ski': 'SKI',
        'snowboard': 'SNOWBOARD',
        'véhicule route': 'CAR',
    }

####################################################################################################

class MoveDirection(MappedEnum):
    CLS = DataType.MoveDirection

    MAP = {
        'montée': 'UP',
        'traversée': 'CROSS',
        'arrêt': 'STOP',
        'descente': 'DOWN',
    }

####################################################################################################

class AlertPerson(MappedEnum):
    CLS = DataType.AlertPerson

    MAP = {
        'autre': 'OTHER',
        'témoin secouriste': 'WITNESS_RESCUER',
        'témoin': 'WITNESS',
        'victime': 'VICTIM',
    }

####################################################################################################

class AlertDevice(MappedEnum):
    CLS = DataType.AlertDevice

    MAP = {
        'autre': 'OTHER',
        'radio': 'RADIO',
        'tél. fixe': 'PHONE',
        'tél.portable': 'CELLPHONE',
    }

####################################################################################################

class StartReason(MappedEnum):
    CLS = DataType.StartReason

    MAP = {
        'accidentelle soi-même': 'SELF',
        'accidentelle tiers': 'THIRD_PARTY',
        'naturelle sérac/corniche': 'SERAC_CORNICE',
        'naturelle': 'NATURAL',
    }

####################################################################################################

class Orientation(MappedEnum):
    CLS = DataType.Orientation

    MAP = {
        'E': 'E',
        'N': 'N',
        'NE': 'NE',
        'NO': 'NW',
        'O': 'W',
        'S': 'S',
        'SE': 'SE',
        'SO': 'SW',
    }

####################################################################################################

class StartType(MappedEnum):
    CLS = DataType.StartType

    MAP = {
        'linéaire': 'LINEAR',
        'ponctuel': 'PONCTUAL',
    }

####################################################################################################

class SnowQuality(MappedEnum):
    CLS = DataType.SnowQuality

    MAP = {
        'humide': 'WET',
        'sèche': 'DRY',
    }

####################################################################################################

class SnowCohesion(MappedEnum):
    CLS = DataType.SnowCohesion

    MAP = {
        'dure': 'HARD',
        'tendre': 'SOFT',
    }

####################################################################################################

class Coordinate:

    """

    sexagesimal degree: degrees, minutes, and seconds : 40° 26′ 46″ N 79° 58′ 56″ W
    degrees and decimal minutes: 40° 26.767′ N 79° 58.933′ W
    decimal degrees: +40.446 -79.982

    """

    _logger = _module_logger.getChild('Coordinate')

    ##############################################

    def __init__(self, value: str) -> None:
        value = value.lower()
        self._logger.info(f"coordinate {value}")
        self._latitude = None
        self._longitude = None
        self._altitude = None
        self.wrong = False
        letter = 't'
        if letter in value:   # UTM
            value = value.replace('/', ' ')
            zone, xy = [_.strip() for _ in value.split(letter)]
            if len(xy) == 14:
                x = xy[:7]
                y = xy[7:]
            else:
                x, y = [_ for _ in xy.split(' ') if _]
            self._longitude, self._latitude = Utm.unproject(int(zone), letter.upper(), int(x), int(y))
        else:   # WGS84
            value = value.replace('/', ' ')
            value = value.replace(",", ".")
            value = value.replace("'.", "'")
            coordinates = [_ for _ in value.split(' ') if _]
            coordinates = [self.tokenise_wgs84(_) for _ in coordinates]
            coordinates = [self.to_decimal(_) for _ in coordinates]
            # coordinates = [self.round(_) for _ in coordinates]
            self._latitude, self._longitude = coordinates[:2]
        if self._bool:
            if self._latitude < self._longitude:
                self._latitude, self._longitude = self._longitude, self._latitude
            if not (40 < self._latitude < 50):
                self._logger.warning(f"Wrong latitude {self}")
                self._latitude = None
                self.wrong = True
            if not (-10 < self._longitude < 10):
                self._logger.warning(f"Wrong longitude {self}")
                self._longitude = None
                self.wrong = True
        if IGN_API and self._bool:
            self._altitude = IGN_API.elevation(latitude=self._latitude, longitude=self._longitude)
        else:
            self._altitude = None

    ##############################################

    # Fixme: clash with: if coordinate
    @property
    def _bool(self) -> bool:
        return not (self._latitude is None or self._longitude is None)

    ##############################################

    @classmethod
    def tokenise_wgs84(cls, coordinate: str) -> list:
        # WGS84: latitude 45°1'2.34"N longitude 6°12.34"E
        parts = []
        part = ''
        def append(value: str) -> None:
            if value:
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
                parts.append(value)
        for c in coordinate:
            if c.isdigit() or c == '.':
                part += c
            else:
                append(part)
                part = ''
        append(part)
        return parts

    ##############################################

    def to_decimal(self, coordinate: list) -> float:
        if not (1 <= len(coordinate) <= 3):
            self._logger.warning(f"Wrong coordinate {coordinate}")
            self.wrong = True
            # raise ValueError("Wrong coordinate %s", str(coordinate))
            if len(coordinate) > 3:
                coordinate = coordinate[:3]
        if len(coordinate) == 3:
            return coordinate[0] + coordinate[1]/60 + coordinate[2]/3600
        if len(coordinate) == 2:
            return coordinate[0] + coordinate[1]/60
        if len(coordinate) == 1:
            value = coordinate[0]
            if isinstance(value, int):
                return None
            return value

    ##############################################

    @classmethod
    def parse_wgs84(cls, value: str) -> list:
        pattern = '(\d+) ° (\d+) \' (\d+(\.\d+)?) "?'.replace(' ', '')
        match = re.match(pattern, value)
        strings = [_ for _ in match.groups()[:3]]
        return [int(strings[0]), int(strings[1]), float(strings[2])]

    ##############################################

    def __repr__(self) -> str:
        return f"latitude: {self._latitude}, longitude: {self._longitude}, altitude: {self._altitude}"

    ##############################################

    @classmethod
    def round(cls, value: float) -> float:
        return round(value, 6)

    ##############################################

    def to_json(self) -> dict:
        if self._bool:
            return {
                'latitude': self.round(self._latitude),
                'longitude': self.round(self._longitude),
                'altitude': self._altitude,
            }
        else:
            return None

####################################################################################################

class Accident(DataAccident):

    _logger = _module_logger.getChild('Accident')

    _MAP = {}

    # Due to pydantic internals, local are picked up as field model...
    @classmethod
    def init(cls):
        for keys, attribute, attribute_cls in (
            (('activité', 'activité récréative'), 'activity', Activity),
            ('altitude', 'altitude', int),
            ('blessées', 'injured', int),
            ('BRA', 'bra_level', int),
            ('cause départ', 'start_reason', StartReason),
            ('code accident', 'code', str),
            (('cohésion neige', 'cohésion'), 'snow_cohesion', SnowCohesion),
            ('commentaires', 'comment', str),
            ('commune', 'city', str),
            (('coordonnées zone départ', 'coordonnées ZD'), 'coordinate', Coordinate),
            ('date', 'date', str),   # to datetime later
            (('décédés', 'décédées'), 'dead', int),
            ('délai intervention', 'rescue_delay', float),
            (('dénivelé (mètres)', 'dénivelé'), 'height_difference', int),
            ('département', 'departement', int),
            (('emportés', 'emportées'), 'carried_away', int),
            ('engin progression', 'gear', Gear),
            ('ensevelis partiels critiques', 'partial_bluried_critical', int),
            ('ensevelis partiels non critiques', 'partial_bluried_non_critical', int),
            ('ensevelis tête', 'head_bluried', int),
            (('ensevelis total', 'enseveli total'), 'full_bluried', int),
            (('épaisseur cassure max. (cm)', 'hauteur maxi cassure'), 'thickness_max', int),
            ('évolution', 'move_direction', MoveDirection),
            ('groupe', 'number_of_persons', int),
            ('heure', 'hour', str),     # to datetime later
            (('inclinaison', 'inclinaison échelle'), 'inclination', Inclination),
            (('indemnes', 'indemne'), 'safe', int),
            (('largeur cassure (mètres)', 'largeur cassure'), 'width', int),
            ('longueur coulée', 'length', int),
            ('massif', 'mountain_area', str),
            ('moyen alerte', 'alert_device', AlertDevice),
            (('orientation', 'exposition'), 'orientation', Orientation),
            ('personne alerte', 'alert_person', AlertPerson),
            ('présence médecin', 'doctor_on_site', bool),
            (('qualité neige', 'TEL'), 'snow_quality', SnowQuality),
            ('site', 'location', str),
            ('type départ', 'start_type', StartType),
        ):
            if isinstance(keys, str):
                keys = (keys,)
            _ = (attribute, attribute_cls)
            for key in keys:
                cls._MAP[key] = _

    ##############################################

    @classmethod
    def learn(cls, sheet: xlrd.sheet) -> None:

        if not hasattr(cls, 'columns'):
            cls.columns = set()
            cls.column_values = {}
        column_map = []
        for i, title in enumerate(sheet.column_titles):
            cls.columns.add((i, title))
            column_map.append(title)
        for row in sheet:
            for i, value in enumerate(row):
                if isinstance(value, str) and not value:
                    continue
                column = column_map[i]
                _ = cls.column_values.setdefault(column, set())
                _.add(value)

    ##############################################

    @classmethod
    def dump(cls) -> None:
        print("Columns by position:")
        for i, name in sorted(cls.columns, key=lambda t: t[0]):
            print(' '*8 + f"({i}, '{name}', '', str),")
        print()
        print("Columns by name:")
        for i, name in sorted(cls.columns, key=lambda t: t[1]):
            print(' '*8 + f"('{name}', '', str, {i}),")
        print()
        print("Column values:")
        for name in sorted(cls.column_values.keys()):
            print(name, cls.column_values[name])

    ##############################################

Accident.init()

####################################################################################################

class AccidentSheetContextManager:

    _logger = _module_logger.getChild('AccidentSheetContextManagergot')

    ##############################################

    def __init__(self, sheet: 'AccidentSheet') -> None:
        self._column_map = [Accident._MAP[_] for _ in sheet.column_titles]

    ##############################################

    def __enter__(self):
        return self

    ##############################################

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    ##############################################

    def convert(self, values: list) -> 'Accident':
        kwargs = {name: None for name, cls in Accident._MAP.values()}
        for i, value in enumerate(values):
            attribute, cls = self._column_map[i]
            if isinstance(value, str):
                value = value.strip()
                if not value:
                    value = None
            if value is not None:
                if issubclass(cls, MappedEnum):
                    value = cls.translate(value)
                elif cls is bool:
                    value = fr_to_bool(value)
                else:
                    value = cls(value)
            kwargs[attribute] = value

        date = kwargs['date']
        hour = kwargs['hour']
        if date:
            date = date.replace('-', '/')
            if hour:
                kwargs['date'] = datetime.datetime.strptime(f"{date} {hour}", '%d/%m/%Y %H:%M')
            else:
                kwargs['date'] = datetime.datetime.strptime(date, '%d/%m/%Y')
            del kwargs['hour']

        rescue_delay = kwargs['rescue_delay']
        if rescue_delay:
            hours = int(rescue_delay)
            # Fixme: ok ???
            minutes = int((rescue_delay - hours) * 100)
            # datetime.timedelta
            kwargs['rescue_delay'] = Delay(hours=hours, minutes=minutes)

        coordinate = kwargs['coordinate']
        if coordinate:
            if coordinate.wrong:
                self._logger.warning(f"Wrong coordinate for {kwargs['code']}")
            kwargs['coordinate'] = coordinate.to_json()

        # pprint(kwargs)
        return Accident(**kwargs)

####################################################################################################

class Victim:

    MAP_2019 = (
        ('code', 'code', str),
        ('n° victime', 'victim_number', int),
        ('departement ', 'fr_departement', int),
        ('commune avalanche', 'avalanche_city', str),
        ('sexe', 'gender', str),
        ('classe âge', 'age_class', str),
        ('nationalité', 'nationality', str),
        ('site résidence', 'living_place', str),
        ('engins progression', 'activity', str),
        ('équipement sécurité', 'security_equipments', str),
        None,
        None,
        None,
        ('ARVA', 'arva', str),
        None,
        ('ABS', 'abs_state', str),
        ('ens. \ntotal', 'full_burial', str),
        ('ens. \npartiel \ncritique', 'partial_critic_burial', str),
        ('ens \npartiel \nnon critique', 'partial_non_critic_burial', str),
        ('durée ens', 'burial_time', str),
        ('profondeur ens', 'burial_depth', str),
        ('sauveteurs', 'rescuers', str),
        ('moyen\nlocalisation', 'localisation_means', str),
        ('état \nvictime', 'victim_state', str),
        ('blessures\nposition corps', 'injury_location', str),
        ('causes décès\nprobable', 'death_cause', str),
        # ('cause particulière \nblessures/décès', '', str),
        # ('cause particulière \nblessures/décès' '', str),
    )

    ##############################################

    @classmethod
    def from_2019(cls, row: list[int | str]) -> 'Victim':

        # map row values to kwargs
        kwargs = {}
        last = None
        for i, map_ in enumerate(cls.MAP_2019):
            value = row[i]
            # match value:
            #     case int() | float():
            #     case str():
            is_str = isinstance(value, str)
            if is_str:
                value = translate_from_fr(value.strip())
            if map_ is not None:
                from_, to, type_cls = map_
                if is_str and not value:
                    kwargs[to] = None
                else:
                    kwargs[to] = type_cls(value)
                last = to
            elif value:
                # append merged-columns
                _ = kwargs[last]
                if not isinstance(_, list):
                    kwargs[last] = [_]    # assumes str
                kwargs[last].append(value)

        print(kwargs)
        obj = cls(**kwargs)

    ##############################################

    def __init__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

####################################################################################################

class AccidentSheet:

    ##############################################

    def __init__(self, sheet: xlrd.sheet) -> None:

        self._sheet = sheet
        # print(f"{sheet.name}, {sheet.nrows}, {sheet.ncols}")
        self._column_titles = [col.value for col in sheet.row(0)]

        # for i in range(sheet.nrows):
        #     for col in sheet.row(i):
        #         print(col.value)

    ##############################################

    @property
    def name(self) -> str:
        return self._sheet.name

    @property
    def column_titles_raw(self) -> Iterator[str]:
        return iter(self._column_titles)

    @property
    def column_titles(self) -> list[str]:
        return [_.replace(os.linesep, ' ').replace('  ', ' ').replace('  ', ' ')
                for _ in self._column_titles]

    ##############################################

    def __len__(self) -> int:
        return self._sheet.nrows

    ##############################################

    def row_values(self, i: int) -> list[int | str]:
        row = self._sheet.row(i)
        values = []
        for cell in row:
            if cell.ctype == 3:
                # _ = xlrd.xldate.xldate_as_datetime(cell.value, 0)
                _ = xlrd.xldate.xldate_as_tuple(cell.value, 0)
                if _[0]:
                    value = f'{_[2]}/{_[1]}/{_[0]}'
                else:
                    value = f'{_[3]}:{_[4]}'
            else:
                value = cell.value
            values.append(value)
        return values

    ##############################################

    def __iter__(self):
        # for row in self._sheet.get_rows():
        for i in range(1, len(self)):
            yield self.row_values(i)

####################################################################################################

class AccidentBook:

    ##############################################

    def __init__(self, path: str | Path) -> None:

        # with open(path) as csvfile:
        #     data = csv.reader(csvfile, delimiter=' ')

        # pd.read_excel(path)

        self._path = path
        match = re.match(r'tableau-accidents-(\d+)-(\d+).xls', path.name)
        self._start_year, self._stop_year = [int(_) for _ in match.groups()]

        self._book = xlrd.open_workbook(path)
        # print(f"The number of worksheets is {self._book.nsheets}")
        # print(f"Worksheet name(s): {self._book.sheet_names()}")
        self._sheets = [AccidentSheet(_) for _ in self._book.sheets()]

    ##############################################

    @property
    def start_year(self):
        return self._start_year

    @property
    def stop_year(self):
        return self._stop_year

    ##############################################

    def __len__(self) -> int:
        return len(self._sheets)

    def __iter__(self) -> Iterator[AccidentSheet]:
        return iter(self._sheets)

    def __getitem__(self, slice_: int | slice) -> AccidentSheet:
        return self._sheets[slice_]

    ##############################################

    def to_accident_pre_2019(self) -> AccidentRegister:
        accidents = AccidentRegister()
        sheet = self[0]
        with AccidentSheetContextManager(sheet) as cm:
            for row in sheet:
                # Skip total line
                if row[0]:
                    accidents += cm.convert(row)
        return accidents
