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

__all__ = [
    'Activity',
    'AlertDevice',
    'AlertPerson',
    'Coordinate',
    'Delay',
    'EnumMixin',
    'Gear',
    'Inclination',
    'MoveDirection',
    'Orientation',
    'SnowCohesion',
    'SnowQuality',
    'StartReason',
    'StartType',
]

####################################################################################################

from enum import Enum, auto

####################################################################################################

class EnumMixin:

    ##############################################

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    ##############################################

    @classmethod
    def validate(cls, value):
        if isinstance(value, cls):
            return value
        elif isinstance(value, str):
            return getattr(cls, value.upper())
        raise TypeError()

    ##############################################

    @classmethod
    def to_json(cls, value) -> str:
        _ = str(value).lower()
        return _.split('.')[1]

####################################################################################################

class Activity(EnumMixin, Enum):
    EDF = auto()
    HIKING = auto()
    HOME = auto()
    HUT_ACCESS = auto()
    MILITARY = auto()
    MINING = auto()
    MOUNTAINEERING = auto()
    OFF_ROAD = auto()
    OTHER = auto()
    ROAD = auto()
    SKI_SLOPE = auto()
    SKI_SLOPE_MAINTENANCE = auto()

####################################################################################################

class Gear(EnumMixin, Enum):
    SKI = auto()
    SNOWBOARD = auto()
    CROSS_COUNTRY_SKIING = auto()
    SNOWSHOE = auto()
    ON_FOOT = auto()
    CAR = auto()

####################################################################################################

class MoveDirection(EnumMixin, Enum):
    UP = auto()
    DOWN = auto()
    CROSS = auto()
    STOP = auto()

####################################################################################################

class AlertPerson(EnumMixin, Enum):
    VICTIM = auto()
    WITNESS = auto()
    WITNESS_RESCUER = auto()
    OTHER = auto()

####################################################################################################

class AlertDevice(EnumMixin, Enum):
    CELLPHONE = auto()
    RADIO = auto()
    PHONE = auto()
    OTHER = auto()

####################################################################################################

class StartReason(EnumMixin, Enum):
    NATURAL = auto()
    SERAC_CORNICE = auto()
    SELF = auto()
    THIRD_PARTY = auto()

####################################################################################################

class Orientation(EnumMixin, Enum):
    N = auto()
    NE = auto()
    E = auto()
    SE = auto()
    S = auto()
    SW = auto()
    W = auto()
    NW = auto()

####################################################################################################

class StartType(EnumMixin, Enum):
    LINEAR = auto()
    PONCTUAL = auto()

####################################################################################################

class SnowQuality(EnumMixin, Enum):
    DRY = auto()
    WET = auto()

####################################################################################################

class SnowCohesion(EnumMixin, Enum):
    SOFT = auto()
    HARD = auto()

####################################################################################################

class Inclination:

    ##############################################

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    ##############################################

    @classmethod
    def validate(cls, value) -> 'Inclination':
        if isinstance(value, cls):
            return value
        elif isinstance(value, str):
            return cls(value)
        raise TypeError('string required')

    ##############################################

    def __init__(self, value: str) -> None:
        self._value = value

    ##############################################

    def __repr__(self) -> str:
        return self._value

    ##############################################

    def to_json(self):
        return self._value

####################################################################################################

class Coordinate:

    ##############################################

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    ##############################################

    @classmethod
    def validate(cls, value) -> 'Coordinate':
        if isinstance(value, cls):
            return value
        elif isinstance(value, str):
            return cls(value=value)
        elif isinstance(value, dict):
            # Fixme: more check ???
            return cls(**value)
        print(value)
        raise TypeError()

    ##############################################

    def __init__(self, latitude: list=None, longitude: list=None, value: str=None ) -> None:
        self._value = value
        self._latidude = latitude
        self._longitude = longitude

    ##############################################

    def __repr__(self) -> str:
        return str(self._value)

    ##############################################

    # @classmethod
    # def format(cls, value) -> str:
    #     return f'{value}'

    ##############################################

    def to_json(self) -> dict:
        if self._longitude:
            return {'longitude': self._longitude, 'latitude': self._latidude}
        else:
            return self._value

####################################################################################################

class Delay:

    ##############################################

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    ##############################################

    @classmethod
    def validate(cls, value) -> 'Delay':
        if isinstance(value, cls):
            return value
        elif isinstance(value, float):
            return cls(minutes=value)
        raise TypeError()

    ##############################################

    def __init__(self, hours: int=0, minutes: int=0) -> None:
        self._minutes = int(hours * 60 + minutes)

    ##############################################

    @property
    def minutes(self) -> int:
        return self._minutes

    ##############################################

    def to_json(self):
        # Fixme: [±]P[DD]DT[HH]H[MM]M[SS]S (ISO 8601 format for timedelta)
        return self.minutes
