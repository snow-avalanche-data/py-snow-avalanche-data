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

"""This module implements a tool to dump a JSON schema by object introspection.

**Known limitations:**

* It doesn't distinguish object dict by type, then it merges all the attributes.

"""

__all__ = ['JsonSchemaInspector', 'SchemaNode']

####################################################################################################

import os

####################################################################################################

class SchemaNode:

    INDENTATION = ' '*4
    STRING_MAX = 500

    ##############################################

    def __init__(self) -> None:
        self._data = None
        self._type = None

    ##############################################

    def __getitem__(self, key: int | str):
        if self._type is 'dict':
            return self._data.setdefault(key, SchemaNode())
        elif self._type is 'list':
            return self._data
        else:
            raise NameError("Schema node is neither a dict or list")

    ##############################################

    def _check_unset(self):
        if self._data is not None:
            raise NameError(f"Schema node has already a type {self._type}")

    ##############################################

    def _init(self, type_, cls) -> None:
        if self._data is None:
            self._type = type_
            self._data = cls()

    ##############################################

    def set_dict(self) -> None:
        self._init('dict', dict)

    ##############################################

    def set_list(self) -> None:
        # self._check_unset()
        self._init('list', SchemaNode)

    ##############################################

    def add_none(self) -> None:
        pass

    ##############################################

    def add_int(self, value: int) -> None:
        self._init('int', set)
        self._data.add(value)

    ##############################################

    def add_float(self, value: float) -> None:
        self._init('float', set)
        self._data.add(value)

    ##############################################

    def add_str(self, value: str) -> None:
        self._init('str', set)
        self._data.add(value.replace(os.linesep, ''))

    ##############################################

    def pprint(self, level: int=0) -> str:
        indent = self.INDENTATION*level
        text = ''
        match self._type:
            case 'int' | 'float':
                inf = min(self._data)
                sup = max(self._data)
                text = f'{{{inf}, {sup}}}'
            case 'str':
                strings = sorted([f"'{_}'" for _ in self._data])
                strings = ', '.join(strings[:20])
                if len(strings) > self.STRING_MAX:
                    strings = "'...'"
                text = '{' + strings + '}'
            case 'list':
                text = self._data.pprint(level+1)
            case 'dict':
                text += f'{indent}{{' + os.linesep
                for key in sorted(self._data.keys()):
                    node = self._data[key]
                    text += f"{indent}{self.INDENTATION}'{key}': "
                    text += node.pprint(level+1).strip()
                    text += ',' + os.linesep
                text += f'{indent}}}' + os.linesep
        return text

####################################################################################################

class JsonSchemaInspector:

    ##############################################

    def __init__(self) -> None:
        self._schema = SchemaNode()

    ##############################################

    def walk(self, data, level: int=0, xpath: list=[]) -> None:
        indent = ' '*4*level
        match data:
            case None:
                # print(f'{indent}{xpath} None')
                self._handle_none(level, xpath, data)
            case int():
                # print(f'{indent}{xpath} int = {data}')
                self._handle_int(level, xpath, data)
            case float():
                # print(f'{indent}{xpath} float = {data}')
                self._handle_float(level, xpath, data)
            case str():
                # print(f'{indent}{xpath} str = "{data[:10]}..."')
                self._handle_str(level, xpath, data)
            case list() | tuple():
                # print(f'{indent}{xpath} list')
                self._handle_list(level, xpath)
                for i, value in enumerate(data):
                    # # print(f'{indent}  - item #{i}')
                    self.walk(value, level+1, xpath + [i])
            case dict():
                # print(f'{indent}{xpath} dict')
                self._handle_dict(level, xpath)
                for key, value in data.items():
                    # print(f'{indent}  - key {key}')
                    self.walk(value, level+1, xpath + [key])
            case _:
                raise ValueError(data)

    ##############################################

    def _xpath_impl(self, xpath: list, node: SchemaNode) -> SchemaNode:
        if xpath:
            key = xpath.pop(0)
            return self._xpath_impl(xpath, node[key])
        else:
            return node

    def xpath(self, xpath: list) -> SchemaNode:
        # , node: Optional[SchemaNode]=None
        # if node is None:
        #     node = self._schema
        return self._xpath_impl(list(xpath), self._schema)

    ##############################################

    def _handle_none(self, level: int, xpath: list, data) -> None:
        node = self.xpath(xpath)
        node.add_none()

    def _handle_int(self, level: int, xpath: list, data) -> None:
        node = self.xpath(xpath)
        node.add_int(data)

    def _handle_float(self, level: int, xpath: list, data) -> None:
        node = self.xpath(xpath)
        node.add_float(data)

    def _handle_str(self, level: int, xpath: list, data) -> None:
        node = self.xpath(xpath)
        node.add_str(data)

    def _handle_list(self, level: int, xpath: list) -> None:
        node = self.xpath(xpath)
        node.set_list()

    def _handle_dict(self, level: int, xpath: list) -> None:
        node = self.xpath(xpath)
        node.set_dict()

    ##############################################

    def inspect(self, json_objects: list) -> None:
        for obj in json_objects:
            self.inspect_object(obj)

        print(self._schema.pprint())

    ##############################################

    def inspect_object(self, obj) -> None:
        self.walk(obj)

####################################################################################################
#
# Original code
#

# keys = set()
# for document in self:
#     keys |= {key for key in document.json.keys()}
# key_values = {key: set() for key in keys}

# for document in self:
#     for key, value in document.json.items():
#         match value:
#             case int() | float() | str():
#                 key_values[key].add(value)
#             case dict():
#                 key_values[key] |= {_ for _ in value.keys()}
#             case list():
#                 if value:
#                     match value[0]:
#                         case str():
#                             key_values[key] |= {_ for _ in value}
#                         case dict():
#                             for lvalue in value:
#                                 key_values[key] |= {_ for _ in lvalue.keys()}

# for key, values in key_values.items():
#     if values:
#         if key in ('date',):
#             dates = sorted(values)
#             key_values[key] = (dates[0], dates[-1])
#         else:
#             if isinstance(list(values)[0], (int, float)):
#                 key_values[key] = (min(values), max(values))

# print('Keys:')
# pprint(key_values)
