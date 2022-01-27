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

"""

TODO: give a look at https://pydantic-docs.helpmanual.io

"""

####################################################################################################

__all__ = [
    'Accident',
    'AccidentRegister',
]

####################################################################################################

from enum import Enum
from pathlib import Path
from typing import Iterator, ClassVar, Optional, List
import datetime
import os

import json
# Faster implementation
# https://github.com/ultrajson/ultrajson
# import ujson
# https://github.com/ijl/orjson

from pydantic import BaseModel

from .DataType import *

####################################################################################################

class Accident(BaseModel):
    activity: Optional[Activity] = None
    altitude: Optional[int] = None
    injured: Optional[int] = None
    bra_level: Optional[int] = None
    start_reason: Optional[StartReason] = None
    code: str
    snow_cohesion: Optional[SnowCohesion] = None
    comment: Optional[str] = None
    city: Optional[str] = None
    coordinate: Optional[Coordinate] = None
    date: Optional[datetime.datetime] = None
    dead: Optional[int] = None
    rescue_delay: Optional[Delay] = None
    height_difference: Optional[int] = None
    departement: Optional[int] = None
    carried_away: Optional[int] = None
    gear: Optional[Gear] = None
    partial_bluried_critical: Optional[int] = None
    partial_bluried_non_critical: Optional[int] = None
    head_bluried: Optional[int] = None
    full_bluried: Optional[int] = None
    thickness_max: Optional[int] = None
    move_direction: Optional[MoveDirection] = None
    number_of_persons: Optional[int] = None
    inclination: Optional[Inclination] = None
    safe: Optional[int] = None
    width: Optional[int] = None
    length: Optional[int] = None
    mountain_area: Optional[str] = None
    alert_device: Optional[AlertDevice] = None
    orientation: Optional[Orientation] = None
    alert_person: Optional[AlertPerson] = None
    doctor_on_site: Optional[bool] = None
    snow_quality: Optional[SnowQuality] = None
    location: Optional[str] = None
    start_type: Optional[StartType] = None

    class Config:
        json_encoders = {
            Coordinate: Coordinate.to_json,
            Delay: Delay.to_json,
            Enum: EnumMixin.to_json,
            Inclination: Inclination.to_json,
        }

    ATTRIBUTE_DOC: ClassVar = {
        'activity': 'activity of the persons during the accident',
        'altitude': 'altitude',
        'injured': 'number of injured persons',
        'bra_level': 'French BRA level',
        'start_reason': 'start reason of the avalanche',
        'code': 'ANENA accident code',
        'snow_cohesion': 'cohesion of the snow',
        'comment': 'comment',
        'city': 'city of the accident',
        'coordinate': 'GPS coordinate',
        'date': 'date',
        'dead': 'number of dead persons',
        'rescue_delay': 'delay for the rescuer to arrive on the accident site',
        'height_difference': 'height difference of the avalanche',
        'departement': 'French departement',
        'carried_away': 'number of carried away persons',
        'gear': 'progression gear used by the group',
        'partial_bluried_critical': 'number of critical partial bluried persons',
        'partial_bluried_non_critical': 'number of non-critical partial bluried  persons',
        'head_bluried': 'number of head bluried persons',
        'full_bluried': 'number of full bluried persons',
        'thickness_max': 'maximum thickness of the avalanche break',
        'move_direction': 'moving direction of the group when the avalanche started',
        'number_of_persons': 'number of persons of the group',
        'inclination': 'inclination of the slope',
        'safe': 'number of safe persons',
        'width': 'width of the avalanche',
        'length': 'length of the avalanche',
        'mountain_area': 'mountain area',
        'alert_device': 'device used to alert',
        'orientation': 'orientation of the slope',
        'alert_person': 'person who alerted',
        'doctor_on_site': 'indicate if a doctor was on site',
        'snow_quality': 'quality of snow',
        'location': 'location of the accident',
        'start_type': 'type of avalanche start',
    }

    ATTRIBUTE_UNIT: ClassVar = {
        'altitude': 'm',
        'rescue_delay': 'min',
        'height_difference': 'm',
        'thickness_max': 'cm',
        'inclination': 'degree',
        'width': 'm',
        'length': 'm',
    }
    for _ in (
        'injured',
        'dead',
        'carried_away',
        'partial_bluried_critical',
        'partial_bluried_non_critical',
        'head_bluried',
        'full_bluried',
        'number_of_persons',
        'safe',
    ):
        ATTRIBUTE_UNIT[_] = 'number of persons'

    ##############################################

    @classmethod
    def field_type(cls, attribute: str):
        return cls.__fields__[attribute].type_

    ##############################################

    @property
    def rescue_delay_minutes(self) -> int:
        if self.rescue_delay is None:
            return None
        return self.rescue_delay.minutes

    ##############################################

    def _ratio(self, value: int | None) -> float:
        if value is None or self.number_of_persons is None:
            return None
        return value / self.number_of_persons * 100

    ##############################################

    # Fixme: cache ??? __getattr__ ???

    @property
    def ratio_injured(self) -> float:
        return self._ratio(self.injured)

    @property
    def ratio_dead(self) -> float:
        return self._ratio(self.dead)

    @property
    def ratio_carried_away(self) -> float:
        return self._ratio(self.carried_away)

    @property
    def ratio_partial_bluried_critical(self) -> float:
        return self._ratio(self.partial_bluried_critical)

    @property
    def ratio_partial_bluried_non_critical(self) -> float:
        return self._ratio(self.partial_bluried_non_critical)

    @property
    def ratio_head_bluried(self) -> float:
        return self._ratio(self.head_bluried)

    @property
    def ratio_full_bluried(self) -> float:
        return self._ratio(self.full_bluried)

    @property
    def ratio_safe(self) -> float:
        return self._ratio(self.safe)

    ##############################################

    @property
    def area(self) -> float:
        if self.length is not None and self.width is not None:
            return self.length * self.width

    @property
    def volume(self) -> float:
        if self.area is not None and self.thickness_max is not None:
            return self.area * self.thickness_max / 100

####################################################################################################

class AccidentList(BaseModel):

    # https://pydantic-docs.helpmanual.io/usage/models/#custom-root-types
    # https://github.com/samuelcolvin/pydantic/issues/675
    # https://github.com/romis2012/pydantic-collections
    __root__: List[Accident] = []

    class Config:
        # Fixme: ???
        json_encoders = Accident.Config.json_encoders

    ##############################################

    def __len__(self) -> int:
        return len(self.__root__)

    def __iter__(self) -> Iterator[Accident]:
        return iter(self.__root__)

    def __getitem__(self, item) -> Accident:
        return self.__root__[item]

    def append(self, accident: Accident) -> None:
        self.__root__.append(accident)

    def extend(self, accident_list: 'AccidentList') -> None:
        self.__root__.extend(accident_list)

####################################################################################################

class AccidentRegister:

    ##############################################

    @classmethod
    def load_json(cls, path: Path) -> 'AccidentRegister':
        with open(path, 'r') as fh:
            data = json.load(fh)
        accidents = cls()
        for accident_data in data:
            accidents += Accident.parse_obj(accident_data)
        return accidents

    ##############################################

    def __init__(self) -> None:
        self._items = AccidentList()

    ##############################################

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[Accident]:
        return iter(self._items)

    def __getitem__(self, i: int) -> Accident:
        return self._items[i]

    ##############################################

    # | 'AccidentRegister'
    def __iadd__(self, item: Accident) -> 'AccidentRegister':
        match item:
            case Accident():
                self._items.append(item)
            case AccidentRegister():
                self._items.extend(item)
        return self

    ##############################################

    def write_json(self, path: Path) -> None:
        with open(path, 'w') as fh:
            dumps_kwargs = dict(
                indent=4,
                ensure_ascii=False,
                sort_keys=True,
            )
            _ = self._items.json(**dumps_kwargs)
            fh.write(_)

    ##############################################

    def and_filter(self, **kwargs) -> 'FilteredAccidentRegister':
        return FilteredAccidentRegister(self, **kwargs)

####################################################################################################

class FilteredAccidentRegister:

    ##############################################

    def __init__(self, parent: AccidentRegister, items=None, **kwargs) -> None:
        self._parent = parent
        if items is not None:
            self._items = list(items)
        else:
            self._items = list(iter(parent))
            if kwargs:
                self.and_filter(**kwargs)

    ##############################################

    @property
    def parent(self):
        return self._parent

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[Accident]:
        return iter(self._items)

    ##############################################

    def and_filter(self, **kwargs) -> None:
        def function(accident: Accident):
            for attribute, attribute_filter in kwargs.items():
                value = getattr(accident, attribute)
                if not attribute_filter(value):
                    return False
            return True
        self._items = list(filter(function, self._items))

    ##############################################

    def __ior__(self, other: 'FilteredAccidentRegister') -> 'FilteredAccidentRegister':
        items = set(iter(self)) | set(iter(other))
        return FilteredAccidentRegister(self.parent, items)

    ##############################################

    def inf_sup(self, attribute: str) -> tuple[int, int]:
        inf = None
        sup = None
        for item in self:
            value = getattr(item, attribute)
            if value is not None:
                if inf is None:
                    inf = value
                    sup = value
                else:
                    inf = min(inf, value)
                    sup = max(sup, value)
        return inf, sup
