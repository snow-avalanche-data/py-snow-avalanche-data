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
    CAR = auto()
    CROSS_COUNTRY_SKIING = auto()
    ON_FOOT = auto()
    SKI = auto()
    SNOWBOARD = auto()
    SNOWSHOE = auto()

####################################################################################################

class MoveDirection(EnumMixin, Enum):
    CROSS = auto()
    DOWN = auto()
    STOP = auto()
    UP = auto()

####################################################################################################

class AlertPerson(EnumMixin, Enum):
    OTHER = auto()
    VICTIM = auto()
    WITNESS = auto()
    WITNESS_RESCUER = auto()

####################################################################################################

class AlertDevice(EnumMixin, Enum):
    CELLPHONE = auto()
    OTHER = auto()
    PHONE = auto()
    RADIO = auto()

####################################################################################################

class StartReason(EnumMixin, Enum):
    NATURAL = auto()
    SELF = auto()
    SERAC_CORNICE = auto()
    THIRD_PARTY = auto()

####################################################################################################

class Orientation(EnumMixin, Enum):
    E = auto()
    N = auto()
    NE = auto()
    NW = auto()
    S = auto()
    SE = auto()
    SW = auto()
    W = auto()

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
    HARD = auto()
    SOFT = auto()

####################################################################################################

class Inclination:

    ##############################################

    def __init__(self, value: str) -> None:
        self._value = value

    ##############################################

    def __repr__(self) -> str:
        return self._value

####################################################################################################

class Coordinate:

    ##############################################

    def __init__(self, value: str) -> None:
        value = value.lower()
        self._value = value
        self._latidude = None
        self._longitude = None

    ##############################################

    def __repr__(self) -> str:
        return self._value

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

    def __init__(self, hours: int=0, minutes: int=0) -> None:
        self._minutes = int(hours * 60 + minutes)

    ##############################################

    @property
    def minutes(self) -> int:
        return self._minutes
