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
    'UTM',
    'WGS84',
    'RGF93',
]

####################################################################################################

import pyproj

####################################################################################################

# WGS 84 -- WGS84 - World Geodetic System 1984, used in GPS
# https://epsg.io/4326
# proj4: +proj=longlat +datum=WGS84 +no_defs
WGS84 = pyproj.Proj(init='epsg:4326')

# RGF93 / Lambert-93 -- France
# https://epsg.io/2154
# proj4:  +proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs
RGF93 = pyproj.Proj(init='epsg:2154')

####################################################################################################

class Utm:

    """UTM to/from WGS84 conversion

    https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system

    The UTM system divides the Earth into 60 zones, each 6° of longitude in width.

    **Latitude bands**
    Each zone is segmented into 20 latitude bands. Each latitude band is 8 degrees high, and is
    lettered starting from "C" at 80°S, increasing up the English alphabet until "X", omitting the
    letters "I" and "O" (because of their similarity to the numerals one and zero). The last
    latitude band, "X", is extended an extra 4 degrees, so it ends at 84°N latitude, thus covering
    the northernmost land on Earth.

    **Exceptions**
    These grid zones are uniform over the globe, except in two areas.

    On the southwest coast of Norway, grid zone 32V (9° of longitude in width) is extended further
    west, and grid zone 31V (3° of longitude in width) is correspondingly shrunk to cover only open
    water.

    Also, in the region around Svalbard, the four grid zones 31X (9° of longitude in width), 33X
    (12° of longitude in width), 35X (12° of longitude in width), and 37X (9° of longitude in width)
    are extended to cover what would otherwise have been covered by the seven grid zones 31X to
    37X. The three grid zones 32X, 34X and 36X are not used.

    """

    # Copyright: https://gist.github.com/twpayne/4409500 twpayne/utm.py

    _projections = {}

    ##############################################

    @classmethod
    def zone(cls, coordinates) -> int:
        lng, lat = coordinates
        # Norway/Svalbard exception
        if 56 <= lat < 64 and 3 <= lng < 12:
            return 32
        if 72 <= lat < 84 and 0 <= lng < 42:
            if lng < 9:
                return 31
            elif lng < 21:
                return 33
            elif lng < 33:
                return 35
            return 37
        return int((lng + 180) / 6) + 1

    ##############################################

    @classmethod
    def letter(cls, coordinates) -> str:
        lng, lat = coordinates
        return 'CDEFGHJKLMNPQRSTUVWXX'[int((lat + 80) / 8)]

    ##############################################

    @classmethod
    def projection(cls, z: str):
        if z not in cls._projections:
            cls._projections[z] = pyproj.Proj(proj='utm', zone=z, ellps='WGS84')
        return cls._projections[z]

    ##############################################

    @classmethod
    def project(cls, coordinates):
        lng, lat = coordinates
        z = cls.zone(coordinates)
        l = cls.letter(coordinates)
        proj = cls.projection(z)
        x, y = proj(lng, lat)
        if y < 0:
            y += 10_000_000
        return z, l, x, y

    ##############################################

    @classmethod
    def unproject(cls, z, l, x, y):
        proj = cls.projection(z)
        if l < 'N':
            y -= 10_000_000
        lng, lat = proj(x, y, inverse=True)
        return (lng, lat)
