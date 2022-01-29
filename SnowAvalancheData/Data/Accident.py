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
    'AccidentDataFrame',
]

####################################################################################################

from enum import Enum
from pathlib import Path
from typing import Iterator, ClassVar, Optional, List
import datetime
import logging
import os

import json
# Faster implementation
# https://github.com/ultrajson/ultrajson
# import ujson
# https://github.com/ijl/orjson

from pydantic import BaseModel
import numpy as np
import pandas as pd

from .DataType import *

####################################################################################################

_module_logger = logging.getLogger(__name__)

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
        'area': 'm2',
        'volume': 'm3',
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

    RATIO_ATTRIBUTES: ClassVar = (
        'injured',
        'dead',
        'carried_away',
        'partial_bluried_critical',
        'partial_bluried_non_critical',
        'head_bluried',
        'full_bluried',
        'safe',
    )

    _logger = _module_logger.getChild('Accident')

    ##############################################

    @classmethod
    def generate_json_schema(cls) -> str:
        # https://pydantic-docs.helpmanual.io/usage/schema/
        # Fixme: ValueError: Value not declarable with JSON Schema, field: name='coordinate' type=Optional[Coordinate] required=False default=None
        return cls.schema_json(indent=4)

    ##############################################

    # Fixme: attribute vs field

    @classmethod
    def attribute_type(cls, attribute: str):
        return cls.__fields__[attribute].type_

    @classmethod
    def attribute_types(cls) -> Iterator[tuple[str, type]]:
        for attribute in Accident.__fields__:
            type_ = Accident.attribute_type(attribute)
            yield attribute, type_

    @classmethod
    def number_attributes(cls) -> Iterator[str]:
        for attribute in cls.__fields__:
            type_ = cls.attribute_type(attribute)
            if type_ in (int, float, Delay):
                yield attribute

    ##############################################

    # def __init__(self, *args, **kwargs) -> None:
    #     super().__init__(*args, **kwargs)
    #     self.check()

    ##############################################

    def check(self) -> bool:
        valid = True
        number_of_persons = self.number_of_persons
        if number_of_persons is not None:
            for attribute in self.RATIO_ATTRIBUTES:
                value = getattr(self, attribute)
                if value is not None and number_of_persons < value:
                    valid = False
                    self._logger.warning("%s > number of persons" % (attribute))
        return valid

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

class AccidentRegisterMixin:

    ##############################################

    def __init___(self) -> None:
        self._items = None

    ##############################################

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[Accident]:
        return iter(self._items)

    def __getitem__(self, i: int) -> Accident:
        return self._items[i]

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

    ##############################################

    def data_frame(self) -> pd.DataFrame:
        return AccidentDataFrame(self)

    ##############################################

    def vectorise(self, attribute: str) -> np.ndarray:
        array = [getattr(self, attribute) for _ in self]
        type_ = Accident.attribute_type(attribute)
        if type_ is int:
            dtype = np.int
        elif type_ is float:
            dtype = np.float
        else:
            return array
        return np.array(array, dtype=dtype)

####################################################################################################

class AccidentRegister(AccidentRegisterMixin):

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

    # | 'AccidentRegister'
    def __iadd__(self, item: Accident) -> 'AccidentRegister':
        match item:
            case Accident():
                self._items.append(item)
            case AccidentRegister():
                self._items.extend(item)
        return self

    ##############################################

    def and_filter(self, **kwargs) -> 'FilteredAccidentRegister':
        return FilteredAccidentRegister(self, **kwargs)

    ##############################################

    def fix(self, path: Path) -> None:
        with open(path, 'r') as fh:
            patches = json.load(fh)
        code_map = {_.code:_ for _ in self}
        for code, patch in patches.items():
            accident = code_map[code]
            for attribute, value in patch.items():
                setattr(accident, attribute, value)

####################################################################################################

class FilteredAccidentRegister(AccidentRegisterMixin):

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

####################################################################################################

class AccidentDataFrame:

    ##############################################

    def __init__(self, register: AccidentRegisterMixin) -> None:
        attributes = [_ for _ in Accident.__fields__ if _ not in ('rescue_delay',)]
        data = {
            attribute: [getattr(_, attribute) for _ in register]
            for attribute in attributes
        }
        df = pd.DataFrame(data)

        df['rescue_delay'] = [_.rescue_delay_minutes for _ in register]

        df['area'] = df['length'] * df['width']
        df['volume'] = df['area'] * df['thickness_max'] / 100
        for attribute in Accident.RATIO_ATTRIBUTES:
            df[f'ratio_{attribute}'] = df[attribute] / df['number_of_persons'] * 100

        self.df = df

    ##############################################

    def inf_sup(self):
        # for attribute in Accident.number_attributes():
        #     print(attribute)
        #     print(self.df.agg({attribute: ['min', 'max']}))
        kwargs = {
            attribute: ['min', 'max']
            for attribute in Accident.number_attributes()
        }
        return self.df.agg(kwargs)

    ##############################################

    def to_csv(self, path: Path) -> None:
        self.df.to_csv(path)

    def to_excel(self, path: Path) -> None:
        """Export to Excel .xlsx file"""
        self.df.to_excel(path, sheet_name='accidents', index=False)

    def to_odf(self, path: Path) -> None:
        # Currently pandas only supports reading OpenDocument spreadsheets.
        raise NotImplementedError

    def to_json(self) -> None:
        return self.df.to_json(orient='records', force_ascii=False)
