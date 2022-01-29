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
from pprint import pprint

from invoke import task

from SnowAvalancheData.Importer.Anena import AccidentBook, AccidentRegister, Accident

####################################################################################################

import SnowAvalancheData.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

def xls_paths() -> list[Path]:
    xls_paths = Path('data', 'anena-xls').glob('tableau-accidents-*-*.xls')
    return sorted(xls_paths)

####################################################################################################

# for path in xls_paths[:-1]:
#     book = AccidentBook(path)
#     Accident.learn(book[0])
# Accident.dump()

####################################################################################################

@task
def to_json(ctx, json_path='anena-accidents.json', fixes_path='data/anena-accidents-fixes.json'):
    accidents = AccidentRegister()
    for path in xls_paths():
        book = AccidentBook(path)
        if book.start_year < 2019:
            print(f'Load {path}')
            accidents += book.to_accident_pre_2019()
    path = Path(json_path)
    print(f'Write {path}')
    accidents.fix(fixes_path)
    accidents.write_json(path)

####################################################################################################

@task
def check(ctx, json_path='anena-accidents.json'):
    accidents = AccidentRegister.load_json(json_path)
    for accident in accidents:
        if not accident.check():
            pprint(accident.dict())
            print()
