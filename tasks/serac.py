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

from pathlib import Path

from invoke import task

from SnowAvalancheData.Importer.Serac import SeracQuery

####################################################################################################

@task
def to_json(ctx, json_path='serac-full.json'):
    serac = SeracQuery()

    json_path = Path(json_path)
    # xtyp=('avalanche', 'person_fall')
    serac.load_from_api()
    serac.write_json(json_path)
