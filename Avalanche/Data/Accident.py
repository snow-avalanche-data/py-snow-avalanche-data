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
    'Accident',
    'Accidents',
]

####################################################################################################

from pathlib import Path
from typing import Iterator
import json

####################################################################################################

class Accident:

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
