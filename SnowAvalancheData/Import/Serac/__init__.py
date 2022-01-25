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

####################################################################################################

from datetime import datetime
from pathlib import Path
from pprint import pprint
from typing import Optional
import json
import math

import requests

####################################################################################################

class CamptocampAPI:

    API_URL = 'https://api.camptocamp.org'
    LIMIT_MAX = 100

    ##############################################

    def __init__(self) -> None:
        pass

    ##############################################

    def get(self, url: list | str, verbose: bool=True, **kwargs) -> dict:
        if not isinstance(url, (list, tuple)):
            url = (url,)
        url = self.API_URL + ''.join(f'/{_}' for _ in url)
        r = requests.get(url, params=kwargs)
        if r.status_code != requests.codes.ok:
            raise NameError(f"API request failed {r.url}")
        if verbose:
            print(f"API request {r.url}")
        return r.json()

    ##############################################

    def list(self, url: str, **kwargs) -> dict:
        data = self.get(url, **kwargs, limit=0)
        number_of_entries = data['total']
        retrieved_number_of_entries = 0
        number_of_queries = int(math.ceil(number_of_entries / self.LIMIT_MAX))
        print(f'number of queries {number_of_queries}')
        documents = []
        for i in range(0, number_of_queries):
            data = self.get(url, **kwargs, offset=i*self.LIMIT_MAX, limit=self.LIMIT_MAX)
            retrieved_number_of_entries += len(data['documents'])
            print(f'Retrieved {retrieved_number_of_entries}/{number_of_entries} entries')
            documents += data['documents']
        return documents

    ##############################################

    # : dict | list
    @classmethod
    def write_json(cls, data, path: Path) -> None:
        with open(path, 'w') as fh:
            json_data = json.dumps(
                data,
                indent=4,
                ensure_ascii=False,
                sort_keys=True,
            )
            fh.write(json_data)

    ##############################################

    @classmethod
    def read_json(cls, path: Path):
        with open(path, 'r') as fh:
            return json.load(fh)

####################################################################################################

class SeracDocumentSchema:
    # attribute = set   means value is in set
    anonymous = bool
    areas = dict
    associations = {
        'articles': None,
        'images': None,
        'outings': None,
        'routes': None,
        'users': None,
        'waypoints': None,
    }
    author = {
        'user_id': int,
        'name': str,
    }
    available_langs = ['en', 'fr', 'it']
    avalanche_level = {
        'level_na',
        'level_1',
        'level_2',
        'level_3',
        'level_4',
        'level_5',
    }
    avalanche_slope = {
        'slope_lt_30',
        'slope_30_35',
        'slope_35_40',
        'slope_40_45',
        'slope_gt_45',
    }
    date = datetime
    disable_comments = bool
    document_id = int
    elevation = int
    event_activity = {
        'alpine_climbing',
        'ice_climbing',
        'multipitch_climbing',
        'other',
        'skitouring',
        'snow_ice_mixed',
        'sport_climbing',
    }
    event_type = {
        'avalanche',
        'blocked_person',
        'crevasse_fall',
        'critical_situation',
        'ice_cornice_collapse',
        'injury_without_fall',
        'other',
        'person_fall',
        'physical_failure',
        'safety_operation',
        'stone_ice_fall',
        'weather_event',
    }
    geometry = {
        'geom': str,
        'geom_detail': None,
        'version': int,
    }
    locales = [
        {
            'title': str,
            'topic_id': int,
            'lang': str,    # language set

            'conditions': str,
            'description': str,
            'group_management': str,
            'increase_impact': str,
            'modifications': str,
            'motivations': str,
            'other_comments': str,
            'place': str,
            'reduce_impact': str,
            'risk': str,
            'route_study': str,
            'safety': str,
            'summary': str,
            'time_management': str,
            'training': str,

            'version': int,
        },
    ]
    nb_impacted = int
    nb_participants = int
    protected = bool
    quality = {
        'empty',
        'draft',
        'medium',
        'fine',
        'great',
    }
    rescue = bool   # or None (Pas d'information)
    severity = {
        'severity_no',
        '1d_to_3d',
        '4d_to_1m',
        '1m_to_3m',
        'more_than_3m',
    }
    type = {'x'}
    version = int

    # Private attributes

    # age = int
    # gender = {'male', 'female'}
    # Implication dans la situation
    # _ = {
    #     'external_witness',
    #     'internal_witness',
    #     'primary_impacted',
    #     'secondary_impacted',
    # }
    # Niveau de pratique
    # _ = {
    #     'non_autonomous',
    #     'autonomous',
    #     'expert',
    # }
    # Fréquence de pratique dans l'activité
    # _ = {
    #     'activity_rate_y5',
    #     'activity_rate_m2',
    #     'activity_rate_w1',
    # }
    # Encadrement
    # _ = {
    #     'no_supervision',
    #     'federal_supervision',
    #     'professional_supervision',
    # }
    # Diplôme d'encadrement pour l'activité
    # _ = {
    #     'federal_supervisor',
    #     'professional_diploma',
    # }
    # Blessures antérieures
    # _ = {
    #     'no',
    #     'previous_injuries_2',
    # }

####################################################################################################

class SeracDocument:

    ##############################################

    def __init__(self, data) -> None:
        self._data = data

    ##############################################

    @property
    def json(self):
        return self._data

    ##############################################

    def xpath(self, *args):
        data = self._data
        for key in args:
            data = data[key]
        return data

    ##############################################

    # anonymous
    # areas
    # associations
    # author
    # available_langs
    # cooked
    # disable_comments
    # locales
    # protected
    # quality
    # type
    # version

    @property
    def avalanche_level(self) -> str:
        # level_1
        # level_2
        # level_3
        # level_4
        # level_na
        return self.xpath('avalanche_level')

    @property
    def avalanche_slope(self) -> str:
        # slope_30_35
        # slope_35_40
        # slope_40_45
        # slope_gt_45
        # slope_lt_30
        return self.xpath('avalanche_slope')

    @property
    def date(self) -> str:
        return datetime.strptime(self.xpath('date'), '%Y-%m-%d')

    @property
    def document_id(self) -> int:
        return self.xpath('document_id')

    @property
    def elevation(self) -> int:
        return self.xpath('elevation')

    @property
    def event_activity(self) -> str:
        # alpine_climbing
        # ice_climbing
        # multipitch_climbing
        # other
        # skitouring
        # snow_ice_mixed
        # sport_climbing
        return self.xpath('event_activity')

    @property
    def event_type(self) -> str:
        # avalanche
        # crevasse_fall
        # other
        # person_fall
        # safety_operation
        # stone_ice_fall
        # weather_event
        return self.xpath('event_type')

    @property
    def nb_impacted(self) -> int:
        return self.xpath('nb_impacted')

    @property
    def nb_participants(self) -> int:
        return self.xpath('nb_participants')

    @property
    def rescue(self) -> bool:
        # None False True
        _ = self.xpath('rescue')
        # Fimxe: ok???
        if _ is None:
            return False
        return _

    @property
    def severity(self) -> str:
        # 1d_to_3d
        # 1m_to_3m
        # 4d_to_1m
        # more_than_3m
        # None
        # severity_no
        return self.xpath('severity')

    @property
    def coordinate(self) -> str:
        # "{\"type\": \"Point\", \"coordinates\": [713257.9299571944, 5623130.402088347]}"
        json_data = self.xpath('geometry', 'geom')
        if json_data is not None:
            data = json.loads(json_data)
            return data['coordinates']
        return None

####################################################################################################

class SeracQuery:

    # Fixme: name
    API_URL = 'xreports'

    ##############################################

    def __init__(self) -> None:
        self._short_documents = []
        self._documents = {}

    ##############################################

    def __len__(self) -> int:
        return len(self._documents)

    def __iter__(self) -> SeracDocument:
        return iter(self._documents.values())

    ##############################################

    def load_from_api(self, **kwargs) -> None:
        self._api = CamptocampAPI()
        payload = {}
        for key in ('xtype', 'act'):
            if key in kwargs:
                value = kwargs[key]
                if isinstance(value, (list, tuple)):
                    value = ','.join(value)
                payload[key] = value
        # filter:
        #  xtyp=stone_ice_fall
        #  qa=draft,great
        #  xalt=2000,9000
        #  l=fr
        #  xpar=1,10
        #  ximp=1,10
        #  xsev=1d_to_3d
        #  q=title
        self._short_documents = self._api.list(url=self.API_URL, **payload)
        self._documents = {}
        self._get_documents()

    ##############################################

    def load_from_json(self, path: Path) -> None:
        data = CamptocampAPI.read_json(path)
        self._short_documents = data['short_documents']
        self._documents = {
            document_id:SeracDocument(document)
            for document_id, document in data['documents'].items()
        }

    ##############################################

    def write_json(self, path: Path) -> None:
        data = {
            'short_documents': self._short_documents,
            'documents': {document_id:document.json for document_id, document in self._documents.items()}
        }
        CamptocampAPI.write_json(data, path)

    ##############################################

    def _get_document(self, document_id: int) -> SeracDocument:
        # cook: process markdown to html
        # , cook='fr'
        data = self._api.get(url=(self.API_URL, document_id), verbose=False)
        return SeracDocument(data)

    ##############################################

    def _get_documents(self):
        document_ids = [document['document_id'] for i, document in enumerate(self._short_documents)]
        number_of_documents = len(document_ids)
        for i, document_id in enumerate(document_ids):
            document = self._get_document(document_id)
            self._documents[document_id] = document
            if i % 100 == 0:
                print(f'Retrieved {i+1}/{number_of_documents}')

    ##############################################

    def scan(self) -> None:
        keys = set()
        for document in self:
            keys |= {key for key in document.json.keys()}
        key_values = {key: set() for key in keys}

        for document in self:
            for key, value in document.json.items():
                match value:
                    case int() | float() | str():
                        key_values[key].add(value)
                    case dict():
                        key_values[key] |= {_ for _ in value.keys()}
                    case list():
                        if value:
                            match value[0]:
                                case str():
                                    key_values[key] |= {_ for _ in value}
                                case dict():
                                    for lvalue in value:
                                        key_values[key] |= {_ for _ in lvalue.keys()}

        for key, values in key_values.items():
            if values:
                if key in ('date',):
                    dates = sorted(values)
                    key_values[key] = (dates[0], dates[-1])
                else:
                    if isinstance(list(values)[0], (int, float)):
                        key_values[key] = (min(values), max(values))

        print('Keys:')
        pprint(key_values)
