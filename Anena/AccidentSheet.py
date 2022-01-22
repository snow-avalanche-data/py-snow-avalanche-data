####################################################################################################

from enum import Enum, auto
from pathlib import Path
from pprint import pprint
from typing import Iterator
import os
import re

# import csv
# import pandas as pd   # requires xlrd
import xlrd

####################################################################################################

FRENCH_TRANSLATION = {
    'français': 'fr',
    'féminin': 'female',
    'masculin': 'male',
    # 'non': False,
    # 'oui': True,
}

def translate_from_fr(string: str) -> str:
    return FRENCH_TRANSLATION.get(string, string)

####################################################################################################

def fr_to_bool(value: str) -> bool:
    match value:
       case 'non':
           return False
       case 'oui':
           return True
    raise ValueError(valueerror)


####################################################################################################

class MappedEnum:
    _subclasses = []
    _map = {}

    ##############################################

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls._subclasses.append(cls)

    ##############################################

    @classmethod
    def _init(cls) -> None:
        for subcls in cls._subclasses:
            subcls._init_map()

    ##############################################

    @classmethod
    def _init_map(cls) -> None:
        map_ = cls.fr_map()
        for key, value in map_.items():
            map_[key] = getattr(cls, value)
        cls._map[cls] = map_

    ##############################################

    @classmethod
    def translate(cls, value: str):
        return cls._map[cls][value]

####################################################################################################

class Activity(MappedEnum, Enum):
    EDF = auto()
    HIKING = auto()
    HOME = auto()
    HUT_ACCESS = auto()
    MILITARY = auto()
    MINING = auto()
    MOUNTAINEERING = auto()
    OFF_ROAD = auto()
    OTHER = auto()
    ROAD = auto()
    SKI_SLOPE = auto()
    SKI_SLOPE_MAINTENANCE = auto()

    @classmethod
    def fr_map(cls) -> dict[str, str]:
        return {
            'accès refuge gardien ski rando': 'HUT_ACCESS',
            'alpinisme': 'MOUNTAINEERING',
            'autre': 'OTHER',
            'entrainement militaire descente couloir': 'MILITARY',
            'equipement piste': 'SKI_SLOPE_MAINTENANCE',
            'habitation': 'HOME',
            'hors-piste': 'OFF_ROAD',
            'minage': 'MINING',
            'piste': 'SKI_SLOPE',
            'randonnée': 'HIKING',
            'relevés EDF / déplacement ski de rando': 'EDF',
            'voie de communication': 'ROAD',
        }

####################################################################################################

class Gear(MappedEnum, Enum):
    CAR = auto()
    CROSS_COUNTRY_SKIING = auto()
    ON_FOOT = auto()
    SKI = auto()
    SNOWBOARD = auto()
    SNOWSHOE = auto()

    @classmethod
    def fr_map(cls) -> dict[str, str]:
        return {
            'à pieds': 'ON_FOOT',
            'raquettes': 'SNOWSHOE',
            'ski fond': 'CROSS_COUNTRY_SKIING',
            'ski': 'SKI',
            'snowboard': 'SNOWBOARD',
            'véhicule route': 'CAR',
        }

####################################################################################################

class MoveDirection(MappedEnum, Enum):
    CROSS = auto()
    DOWN = auto()
    STOP = auto()
    UP = auto()

    @classmethod
    def fr_map(cls) -> dict[str, str]:
        return {
            'montée': 'UP',
            'traversée': 'CROSS',
            'arrêt': 'STOP',
            'descente': 'DOWN',
        }

####################################################################################################

class AlertPerson(MappedEnum, Enum):
    OTHER = auto()
    VICTIM = auto()
    WITNESS = auto()
    WITNESS_RESCUER = auto()

    @classmethod
    def fr_map(cls) -> dict[str, str]:
        return {
            'autre': 'OTHER',
            'témoin secouriste': 'WITNESS_RESCUER',
            'témoin': 'WITNESS',
            'victime': 'VICTIM',
        }

####################################################################################################

class AlertDevice(MappedEnum, Enum):
    CELLPHONE = auto()
    OTHER = auto()
    PHONE = auto()
    RADIO = auto()

    @classmethod
    def fr_map(cls) -> dict[str, str]:
        return {
            'autre': 'OTHER',
            'radio': 'RADIO',
            'tél. fixe': 'PHONE',
            'tél.portable': 'CELLPHONE',
        }

####################################################################################################

class StartReason(MappedEnum, Enum):
    NATURAL = auto()
    SELF = auto()
    SERAC_CORNICE = auto()
    THIRD_PARTY = auto()

    @classmethod
    def fr_map(cls) -> dict[str, str]:
        return {
            'accidentelle soi-même': 'SELF',
            'accidentelle tiers': 'THIRD_PARTY',
            'naturelle sérac/corniche': 'SERAC_CORNICE',
            'naturelle': 'NATURAL',
        }

####################################################################################################

class Orientation(MappedEnum, Enum):
    E = auto()
    N = auto()
    NE = auto()
    NW = auto()
    S = auto()
    SE = auto()
    SW = auto()
    W = auto()

    @classmethod
    def fr_map(cls) -> dict[str, str]:
        return {
            'E': 'E',
            'N': 'N',
            'NE': 'NE',
            'NO': 'NW',
            'O': 'W',
            'S': 'S',
            'SE': 'SE',
            'SO': 'SW',
        }

####################################################################################################

class StartType(MappedEnum, Enum):
    LINEAR = auto()
    PONCTUAL = auto()

    @classmethod
    def fr_map(cls) -> dict[str, str]:
        return {
            'linéaire': 'LINEAR',
            'ponctuel': 'PONCTUAL',
        }

####################################################################################################

class SnowQuality(MappedEnum, Enum):
    DRY = auto()
    WET = auto()

    @classmethod
    def fr_map(cls) -> dict[str, str]:
        return {
            'humide': 'WET',
            'sèche': 'DRY',
        }

####################################################################################################

class SnowCohesion(MappedEnum, Enum):
    HARD = auto()
    SOFT = auto()

    @classmethod
    def fr_map(cls) -> dict[str, str]:
        return {
            'dure': 'HARD',
            'tendre': 'SOFT',
        }

####################################################################################################

MappedEnum._init()

####################################################################################################

class Accident:

    _MAP = {}
    for keys, attribute, cls in (
        (('activité', 'activité récréative'), 'activity', Activity),
        ('altitude', 'altitude', int),
        ('blessées', 'injured', int),
        ('BRA', 'bra_level', int),
        ('cause départ', 'start_reason', StartReason),
        ('code accident', 'code', str),
        (('cohésion neige', 'cohésion'), 'snow_cohesion', SnowCohesion),
        ('commentaires', 'comment', str),
        ('commune', 'city', str),
        (('coordonnées zone départ', 'coordonnées ZD'), 'coordinate', str),
        ('date', 'date', str),
        (('décédés', 'décédées'), 'dead', int),
        ('délai intervention', 'rescue_delay', float),
        (('dénivelé (mètres)', 'dénivelé'), 'height_difference', int),
        ('département', 'departement', int),
        (('emportés', 'emportées'), 'carried_away', int),
        ('engin progression', 'gear', Gear),
        ('ensevelis partiels critiques', 'partial_bluried_critical', int),
        ('ensevelis partiels non critiques', 'partial_bluried_non_critical', int),
        ('ensevelis tête', 'head_bluried', int),
        (('ensevelis total', 'enseveli total'), 'full_bluried', int),
        (('épaisseur cassure max. (cm)', 'hauteur maxi cassure'), 'thickness_max', int),
        ('évolution', 'move_direction', MoveDirection),
        ('groupe', 'number_of_persons', int),
        ('heure', 'hour', str),
        (('inclinaison', 'inclinaison échelle'), 'inclination', str),
        (('indemnes', 'indemne'), 'safe', int),
        (('largeur cassure (mètres)', 'largeur cassure'), 'width', int),
        ('longueur coulée', 'length', int),
        ('massif', 'mountain_area', str),
        ('moyen alerte', 'alert_device', AlertDevice),
        (('orientation', 'exposition'), 'orientation', Orientation),
        ('personne alerte', 'alert_person', AlertPerson),
        ('présence médecin', 'doctor_on_site', bool),
        (('qualité neige', 'TEL'), 'snow_quality', SnowQuality),
        ('site', 'location', str),
        ('type départ', 'start_type', StartType),
    ):
        if isinstance(keys, str):
            keys = (keys,)
        _ = (attribute, cls)
        for key in keys:
            _MAP[key] = _

    ##############################################

    @classmethod
    def column_map(cls, columns: list[str]) -> list[tuple]:   # tuple[str, ctor]
        # Fixme: use a context manager ?
        return [cls._MAP[_] for _ in columns]

    @classmethod
    def convert(cls, column_map: list, values: list) -> 'Accident':
        kwargs = {}
        for i, value in enumerate(values):
            attribute, cls = column_map[i]
            if isinstance(value, str):
                value = value.strip()
                if not value:
                    value = None
            if value is not None:
                if issubclass(cls, MappedEnum):
                    value = cls.translate(value)
                elif cls in (int, float):
                    value = cls(value)
                elif cls is bool:
                    value = fr_to_bool(value)
            kwargs[attribute] = value
        pprint(kwargs)
        # return Accident(**kwargs)

    ##############################################

    @classmethod
    def learn(cls, sheet: xlrd.sheet) -> None:

        if not hasattr(cls, 'columns'):
            cls.columns = set()
            cls.column_values = {}
        column_map = []
        for i, title in enumerate(sheet.column_titles):
            cls.columns.add((i, title))
            column_map.append(title)
        for row in sheet:
            for i, value in enumerate(row):
                if isinstance(value, str) and not value:
                    continue
                column = column_map[i]
                _ = cls.column_values.setdefault(column, set())
                _.add(value)

    ##############################################

    @classmethod
    def dump(cls) -> None:
        print("Columns by position:")
        for i, name in sorted(cls.columns, key=lambda t: t[0]):
            print(' '*8 + f"({i}, '{name}', '', str),")
        print()
        print("Columns by name:")
        for i, name in sorted(cls.columns, key=lambda t: t[1]):
            print(' '*8 + f"('{name}', '', str, {i}),")
        print()
        print("Column values:")
        for name in sorted(cls.column_values.keys()):
            print(name, cls.column_values[name])

    ##############################################

    def __init__(self, **kwargs: dict) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

####################################################################################################

class Victim:

    MAP_2019 = (
        ('code', 'code', str),
        ('n° victime', 'victim_number', int),
        ('departement ', 'fr_departement', int),
        ('commune avalanche', 'avalanche_city', str),
        ('sexe', 'gender', str),
        ('classe âge', 'age_class', str),
        ('nationalité', 'nationality', str),
        ('site résidence', 'living_place', str),
        ('engins progression', 'activity', str),
        ('équipement sécurité', 'security_equipments', str),
        None,
        None,
        None,
        ('ARVA', 'arva', str),
        None,
        ('ABS', 'abs_state', str),
        ('ens. \ntotal', 'full_burial', str),
        ('ens. \npartiel \ncritique', 'partial_critic_burial', str),
        ('ens \npartiel \nnon critique', 'partial_non_critic_burial', str),
        ('durée ens', 'burial_time', str),
        ('profondeur ens', 'burial_depth', str),
        ('sauveteurs', 'rescuers', str),
        ('moyen\nlocalisation', 'localisation_means', str),
        ('état \nvictime', 'victim_state', str),
        ('blessures\nposition corps', 'injury_location', str),
        ('causes décès\nprobable', 'death_cause', str),
        # ('cause particulière \nblessures/décès', '', str),
        # ('cause particulière \nblessures/décès' '', str),
    )

    ##############################################

    @classmethod
    def from_2019(cls, row: list[int | str]) -> 'Victim':

        # map row values to kwargs
        kwargs = {}
        last = None
        for i, map_ in enumerate(cls.MAP_2019):
            value = row[i]
            # match value:
            #     case int() | float():
            #     case str():
            is_str = isinstance(value, str)
            if is_str:
                value = translate_from_fr(value.strip())
            if map_ is not None:
                from_, to, type_cls = map_
                if is_str and not value:
                    kwargs[to] = None
                else:
                    kwargs[to] = type_cls(value)
                last = to
            elif value:
                # append merged-columns
                _ = kwargs[last]
                if not isinstance(_, list):
                    kwargs[last] = [_]    # assumes str
                kwargs[last].append(value)

        print(kwargs)
        obj = cls(**kwargs)

    ##############################################

    def __init__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

####################################################################################################

class AccidentSheet:

    ##############################################

    def __init__(self, sheet: xlrd.sheet) -> None:

        self._sheet = sheet
        # print(f"{sheet.name}, {sheet.nrows}, {sheet.ncols}")
        self._column_titles = [col.value for col in sheet.row(0)]

        # for i in range(sheet.nrows):
        #     for col in sheet.row(i):
        #         print(col.value)

    ##############################################

    @property
    def name(self) -> str:
        return self._sheet.name

    @property
    def column_titles_raw(self) -> Iterator[str]:
        return iter(self._column_titles)

    @property
    def column_titles(self) -> list[str]:
        return [_.replace(os.linesep, ' ').replace('  ', ' ').replace('  ', ' ')
                for _ in self._column_titles]

    def __len__(self) -> int:
        return self._sheet.nrows

    def row_values(self, i: int) -> list[int | str]:
        return [_.value for _ in self._sheet.row(i)]

    def __iter__(self):
        # for row in self._sheet.get_rows():
        for i in range(1, len(self)):
            yield self.row_values(i)

####################################################################################################

class AccidentBook:

    ##############################################

    def __init__(self, path: str | Path) -> None:

        # with open(path) as csvfile:
        #     data = csv.reader(csvfile, delimiter=' ')

        # pd.read_excel(path)

        self._path = path
        match = re.match(r'tableau-accidents-(\d+)-(\d+).xls', path.name)
        self._start_year, self._stop_year = [int(_) for _ in match.groups()]

        self._book = xlrd.open_workbook(path)
        # print(f"The number of worksheets is {self._book.nsheets}")
        # print(f"Worksheet name(s): {self._book.sheet_names()}")
        self._sheets = [AccidentSheet(_) for _ in self._book.sheets()]

    ##############################################

    @property
    def start_year(self):
        return self._start_year

    @property
    def stop_year(self):
        return self._stop_year

    ##############################################

    def __len__(self) -> int:
        return len(self._sheets)

    def __iter__(self) -> Iterator[AccidentSheet]:
        return iter(self._sheets)

    def __getitem__(self, slice_: int | slice) -> AccidentSheet:
        return self._sheets[slice_]

    ##############################################

    def to_accident_pre_2019(self):
        sheet = self[0]
        column_map = Accident.column_map(sheet.column_titles)
        for row in sheet:
            Accident.convert(column_map, row)

####################################################################################################

if __name__ == '__main__':

    xls_paths = Path('xls').glob('tableau-accidents-*-*.xls')
    xls_paths = sorted(xls_paths)

    if False:
        for path in xls_paths[:-1]:
            book = AccidentBook(path)
            Accident.learn(book[0])
        Accident.dump()

    if True:
        for path in xls_paths:
            book = AccidentBook(path)
            if book.start_year < 2019:
                print(book.start_year)
                book.to_accident_pre_2019()

        # for sheet in book[0]:
            # print(sheet.name)
            # print(sheet.column_titles)
        # sheet = book[1]
        # for row in sheet:
        #     anena_victim = Victim.from_2019(row)
