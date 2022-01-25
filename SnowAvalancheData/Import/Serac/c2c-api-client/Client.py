####################################################################################################
#
# C2cApiClient - A Python client for the camptocamp.org API
# Copyright (C) 2017 Salvaire Fabrice
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################

import datetime
import requests
import logging

####################################################################################################

class ClientLogin:

    ##############################################

    def __init__(self, username, password):

        self.username = username
        self.password = password

####################################################################################################

class LoginData:

    ##############################################

    def __init__(self, json):

        self._language = json['lang']
        self._expire = datetime.datetime.fromtimestamp(json['expire'])
        self._id = json['id']
        self._token = json['token']
        self._forum_username = json['forum_username']
        self._name = json['name']
        self._roles = json['roles']
        self._redirect_interval = json['redirect_internal']
        self._username = json['username']

    ##############################################

    @property
    def language(self):
        return self._language

    @property
    def expire(self):
        return self._expire

    @property
    def expired(self):
        return datetime.datetime.now() >= self._expire

    @property
    def id(self):
        return self._id

    @property
    def token(self):
        return self._token

    @property
    def forum_username(self):
        return self._forum_username

    @property
    def name(self):
        return self._name

    @property
    def roles(self):
        return self._roles

    @property
    def redirect_internal(self):
        return self._redirect_interval

    @property
    def username(self):
        return self._username

####################################################################################################

class SearchSettings:

    ##############################################

    def __init__(self,
                 language='fr',
                 limit=7,
                 area=False,
                 article=False,
                 book=False,
                 image=False,
                 map_=False,
                 outing=False,
                 route=False,
                 userprofile=False,
                 waypoint=False,
                 xreport=False,
    ):

        self._limit = limit
        self._language = language

        self._area = area
        self._article = article
        self._book = book
        self._image = image
        self._map = map_
        self._outing = outing
        self._route = route
        self._userprofile = userprofile
        self._waypoint = waypoint
        self._xreport = xreport

    ##############################################

    @property
    def language(self):
        return self._language

    @language.setter
    def language(self, value):
        self._language = value


    @property
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, value):
        self._limit = value


    @property
    def area(self):
        return self._area

    @area.setter
    def area(self, value):
        self._area = value


    @property
    def article(self):
        return self._article

    @article.setter
    def article(self, value):
        self._article = value


    @property
    def book(self):
        return self._book

    @book.setter
    def book(self, value):
        self._book = value


    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        self._image = value


    @property
    def map(self):
        return self._map

    @map.setter
    def map(self, value):
        self._map = value


    @property
    def outing(self):
        return self._outing

    @outing.setter
    def outing(self, value):
        self._outing = value


    @property
    def route(self):
        return self._route

    @route.setter
    def route(self, value):
        self._route = value


    @property
    def userprofile(self):
        return self._userprofile

    @userprofile.setter
    def userprofile(self, value):
        self._userprofile = value


    @property
    def waypoint(self):
        return self._waypoint

    @waypoint.setter
    def waypoint(self, value):
        self._waypoint = value


    @property
    def xreport(self):
        return self._xreport

    @xreport.setter
    def xreport(self, value):
        self._xreport = value

    ##############################################

    @property
    def type_letters(self):
        letters = []
        if self._area:
            letters.append('a')
        if self._article:
            letters.append('c')
        if self._book:
            letters.append('b')
        if self._image:
            letters.append('i')
        if self._map:
            letters.append('m')
        if self._outing:
            letters.append('o')
        if self._route:
            letters.append('r')
        if self._userprofile:
            letters.append('u')
        if self._xreport:
            letters.append('x')
        if self._waypoint:
            letters.append('w')
        return ','.join(letters)

####################################################################################################

class VersionedObject:

    ##############################################

    def __init__(self, json):

        self._version = json['version']

    ##############################################

    @property
    def version(self):
        return self._version

####################################################################################################

class TypedObject(VersionedObject):

    ##############################################

    def __init__(self, json):

        VersionedObject.__init__(self, json)
        self._type = json['type']

    ##############################################

    @property
    def type(self):
        return self._type

####################################################################################################

class Client:

    _logger = logging.getLogger(__name__ + '.Client')

    API_URL = 'https://api.camptocamp.org'

    TYPE_TO_URL = {
        'a': 'areas',
        'c': 'articles',
        'b': 'books',
        'i': 'images',
        'm': 'maps',
        'o': 'outings',
        'r': 'routes',
        'u': 'userprofiles',
        'x': 'xreports',
        'w': 'waypoints',
    }

    ##############################################

    def __init__(self, client_login=None):

        self._login_data = None

        self._client_login = client_login
        if client_login is not None:
            self.login()

    ##############################################

    def _make_url(self, *args):

        return self.API_URL + '/' + '/'.join(args)

    ##############################################

    def _make_url_for_document(self, document):

        return self._make_url(self.TYPE_TO_URL[document['type']], str(document['document_id']))

    ##############################################

    def _headers_for_authorization(self):

        headers = {}
        if self.logged:
            headers['Authorization'] = 'JWT token="{}"'.format(self._login_data.token)
        return headers

    ##############################################

    def _check_json_response(self, response):

        response.raise_for_status()

        json = response.json()
        self._logger.debug(json)
        if 'status' in json and json['status'] == 'error':
            # {'status': 'error', 'errors': [{'name': 'user', 'location': 'body', 'description': 'Login failed'}]}
            for error in json['errors']:
                self._logger.error(error['description'])
            return None
        else:
            return json

    ##############################################

    def _post_put(self, url, payload, requests_method):

        if not self.logged:
            return
        self.update_login()
        r = requests_method(url, headers=self._headers_for_authorization(), json=payload)
        r.raise_for_status()

    ##############################################

    def _post(self, url, payload):

        self._post_put(url, payload, requests.post)

    ##############################################

    def _put(self, url, payload):

        self._post_put(url, payload, requests.put)

    ##############################################

    def health(self):

        """Query the health of the REST API service"""

        url = self._make_url('health')
        r = requests.get(url)
        return self._check_json_response(r)

    ##############################################

    def login(self, remember=True, discourse=True):

        self._logger.info('Login to camptocamp.org with user {} ...'.format(self._client_login.username))
        payload = {
            'username': self._client_login.username,
            'password': self._client_login.password,
            'remember': remember,
            'discourse': discourse,
        }
        url = self._make_url('users', 'login')
        r = requests.post(url, json=payload)
        json = self._check_json_response(r)
        if json is not None:
            self._login_data = LoginData(json)
            self._logger.info("Logged successfully, connection will expire at {}".format(self._login_data.expire))
        else:
            self._login_data = None

    ##############################################

    @property
    def logged(self):
        return self._login_data is not None

    ##############################################

    def update_login(self):

        if self.logged and self._login_data.expired:
            self._logger.info("Login expired")
            self.login()

    ##############################################

    def area(self, document_id):

        url = self._make_url('areas', str(document_id))
        r = requests.get(url)
        return self._check_json_response(r)

    ##############################################

    def article(self, document_id):

        url = self._make_url('articles', str(document_id))
        r = requests.get(url)
        return self._check_json_response(r)

    ##############################################

    def image(self, document_id):

        url = self._make_url('images', str(document_id))
        r = requests.get(url)
        return self._check_json_response(r)

    ##############################################

    def map(self, document_id):

        url = self._make_url('maps', str(document_id))
        r = requests.get(url)
        return self._check_json_response(r)

    ##############################################

    def outing(self, document_id):

        url = self._make_url('outings', str(document_id))
        r = requests.get(url)
        return self._check_json_response(r)

    ##############################################

    def route(self, document_id):

        url = self._make_url('routes', str(document_id))
        r = requests.get(url)
        return self._check_json_response(r)

    ##############################################

    def user_profile(self, user_id=None):

        if user_id is None:
            if self.logged:
                user_id = self._login_data.id
            else:
                return None
        url = self._make_url('profiles', str(user_id))
        r = requests.get(url)
        return self._check_json_response(r)

    ##############################################

    def xreport(self, document_id):

        url = self._make_url('xreports', str(document_id))
        r = requests.get(url)
        return self._check_json_response(r)

    ##############################################

    def waypoint(self, document_id):

        url = self._make_url('waypoints', str(document_id))
        r = requests.get(url)
        return self._check_json_response(r)

    ##############################################

    def search(self, search_string, settings=None):

        """Search documents

        cf. https://github.com/c2corg/v6_api/blob/master/c2corg_api/views/search.py

        Request:
            `GET` `/search?q=...[&lang=...][&limit=...][&t=...]`

        Parameters:
            `q=...`
            The search word.

            `lang=...` (optional)
            When set only the given locale will be included (if available).
            Otherwise all locales will be returned.

            `limit=...` (optional)
            How many results should be returned per document type
            (default: 10). The maximum is 50.

            `t=...` (optional)
            Which document types should be included in the search. If not
            given, all document types are returned. Example: `...&t=w,r`
            searches only for waypoints and routes.
        """

        if settings is None:
            settings = SearchSettings()
        url = self._make_url('search')
        parameters = {
            'q': search_string,
            'pl': settings.language, # lang ???
            'limit': settings.limit,
            't': settings.type_letters,
        }
        r = requests.get(url, params=parameters)
        return self._check_json_response(r)

    ##############################################

    def post(self, document):

        url = self._make_url_for_document(document)
        self._post(url, document)

    ##############################################

    def update(self, message, document):

        url = self._make_url_for_document(document)
        payload = {'message': message, 'document': document}
        self._put(url, payload)
