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
    'Accident',
    'Accidents',
]

####################################################################################################

from enum import Enum
from pathlib import Path
from typing import Iterator
import datetime
import json

from .DataType import *

####################################################################################################

class Accident:

    ATTRIBUTE_TYPES = {
        'activity': Activity,
        'altitude': int,
        'injured': int,
        'bra_level': int,
        'start_reason': StartReason,
        'code': str,
        'snow_cohesion': SnowCohesion,
        'comment': str,
        'city': str,
        'coordinate': Coordinate,
        'date': datetime.datetime,
        'dead': int,
        'rescue_delay': float,
        'height_difference': int,
        'departement': int,
        'carried_away': int,
        'gear': Gear,
        'partial_bluried_critical': int,
        'partial_bluried_non_critical': int,
        'head_bluried': int,
        'full_bluried': int,
        'thickness_max': int,
        'move_direction': MoveDirection,
        'number_of_persons': int,
        'inclination': Inclination,
        'safe': int,
        'width': int,
        'length': int,
        'mountain_area': str,
        'alert_device': AlertDevice,
        'orientation': Orientation,
        'alert_person': AlertPerson,
        'doctor_on_site': bool,
        'snow_quality': SnowQuality,
        'location': str,
        'start_type': StartType,
    }

    ATTRIBUTE_DOC = {
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

    ##############################################

    @classmethod
    def from_json(cls, data: dict) -> 'Accident':
        kwargs = {}
        for key, value in data.items():
            if value is not None:
                value_cls = cls.ATTRIBUTE_TYPES[key]
                if value_cls is Coordinate:
                    if isinstance(value, str):
                        value = Coordinate(value=value)
                    else:
                        value = Coordinate(**value)
                elif value_cls is datetime.datetime:
                    value = datetime.datetime.fromisoformat(value)
                elif value_cls is Delay:
                    value = Delay(minutes=value)
                elif issubclass(value_cls, Enum):
                    value = getattr(value_cls, value.upper())
                else:
                    value = value_cls(value)
            kwargs[key] = value
        return cls(**kwargs)

    ##############################################

    def __init__(self, **kwargs: dict) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    ##############################################

    @property
    def week(self) -> int:
        return self.date.isocalendar().week

    ##############################################

    def to_json(self) -> dict:
        return self.__dict__

####################################################################################################

class Accidents:

    JSON_ENCODER = None

    ##############################################

    @classmethod
    def load_json(cls, path: Path) -> 'Accidents':
        with open(path, 'r') as fh:
            data = json.load(fh)
        accidents = cls()
        for accident_data in data:
            accidents += Accident.from_json(accident_data)
        return accidents

    ##############################################

    def __init__(self) -> None:
        self._items = []

    ##############################################

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[Accident]:
        return iter(self._items)

    ##############################################

    # | 'Accidents'
    def __iadd__(self, item: Accident) -> 'Accidents':
        match item:
            case Accident():
                self._items.append(item)
            case Accidents():
                self._items.extend(item)
        return self

    ##############################################

    def to_json(self) -> list:
        return [_.to_json() for _ in self]

    ##############################################

    def write_json(self, path: Path) -> None:
        with open(path, 'w') as fh:
            data = json.dumps(
                self.to_json(),
                cls=self.JSON_ENCODER,
                indent=4,
                ensure_ascii=False,
                sort_keys=True,
            )
            fh.write(data)

    ##############################################

    def and_filter(self, **kwargs) -> 'FilteredAccidents':
        return FilteredAccidents(self, **kwargs)

####################################################################################################

class FilteredAccidents:

    ##############################################

    def __init__(self, parent: Accidents, items=None, **kwargs) -> None:
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

    def __ior__(self, other: 'FilteredAccidents') -> 'FilteredAccidents':
        items = set(iter(self)) | set(iter(other))
        return FilteredAccidents(self.parent, items)

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
