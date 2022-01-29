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
    'IgnApi',
]

####################################################################################################

from pathlib import Path
import json
import logging

import requests

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

# curl
#   'https://wxs.ign.fr/an7nvfzojv5wa96dsga5nk8w/alti/rest/elevation.json?lon=0.2367|2.1570&lat=48.0551|46.6077&indent=true'
#   -H 'Origin: https://www.geoportail.gouv.fr'
#   -H 'User-Agent: Mozilla/5.0 (Fedora; Linux; rv:95.0)'
#
# {"elevations": [
#   {
#     "lon": 0.2367,
#     "lat": 48.0551,
#     "z": 96.53,
#     "acc": 2.5
#   },
#   {
#     "lon": 2.157,
#     "lat": 46.6077,
#     "z": 208.77,
#     "acc": 2.5
#   }

####################################################################################################

class IgnApi:

    URL = 'https://wxs.ign.fr'

    _logger = _module_logger.getChild('IgnApi')

    ##############################################

    @classmethod
    def from_json_settings(cls, path: Path) -> 'IgnApi':
        cls._logger.info(f"Load {path}")
        with open(path, 'r') as fh:
            kwargs = json.load(fh)
        return cls(**kwargs)

    ##############################################

    def __init__(self, api_key: str, origin: str, user_agent: str) -> None:
        self._api_key = api_key
        self._origin = origin
        self._user_agent = user_agent

    ##############################################

    def get(self, url: str, payload: dict) -> requests.request:
        url = f'{self.URL}/{self._api_key}/{url}'
        headers = {
            'Origin': self._origin,
            'User-Agent': self._user_agent,
        }
        r = requests.get(url, headers=headers, params=payload)
        self._logger.info(r.url)
        return r

    ##############################################

    def elevation(self, latitude: float, longitude: float) -> float:
        url = 'alti/rest/elevation.json'
        payload = {
            'lat': latitude,
            'lon': longitude,
        }
        r = self.get(url, payload)
        data = r.json()
        print(data)
        return data['elevations'][0]['z']

    ##############################################

    def elevation_line(self, coordinates: list[list[float, float]], sampling: int=200):
        # https://wxs.ign.fr/an7nvfzojv5wa96dsga5nk8w/alti/rest/elevationLine.xml?gp-access-lib=3.0.3&lon=5.86722018|5.93640326&lat=45.13735592|45.10597431&indent=false&crs='CRS:84'&sampling=200
        url = 'alti/rest/elevationLine.json'
        def join_float(i):
            return '|'.join([str(float(_[i])) for _ in coordinates])
        payload = {
            'lat': join_float(0),
            'lon': join_float(1),
            'indent': 'false',
            'crs': 'CRS:84',
            'sampling': str(int(sampling)),
        }
        r = self.get(url, payload)
        data = r.json()
        return data
