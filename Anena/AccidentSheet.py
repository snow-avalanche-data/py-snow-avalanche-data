####################################################################################################

from enum import Enum, auto
from pathlib import Path
from pprint import pprint
from typing import Iterator
import datetime
import json
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
    raise ValueError(value)

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

    ##############################################

    @classmethod
    def to_json(cls, value) -> str:
        _ = str(value).lower()
        return _.split('.')[1]

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

class Inclination:

    ##############################################

    def __init__(self, value: str) -> None:
        self._value = value

    ##############################################

    def __repr__(self) -> str:
        return self._value

####################################################################################################

class Coordinate:

    ##############################################

    def __init__(self, value: str) -> None:
        value = value.lower()
        self._value = value
        self._latidude = None
        self._longitude = None
        if '°' in value:
            # 45°51'23.50" / 6°27'12.10"
            value = value.replace('/', ' ')
            value = value.replace("''", '"')
            value = value.replace("'.", "'")
            # Fixme:
            #   45°03.931'' // 6°04.543'
            #   45°24'16''/6°49'01.2'' /// 45°24'05.8''/6°49'02.6''
            try:
                self._latidude, self._longitude = [self.parse_coordinate(_) for _ in value.split(' ') if _]
            except Exception:
                pass

    ##############################################

    @classmethod
    def parse_coordinate(cls, value: str) -> list:
        match = re.match('(\d+)°(\d+)\'(\d+(\.\d+)?)"?', value)
        strings = [_ for _ in match.groups()[:3]]
        return [int(strings[0]), int(strings[1]), float(strings[2])]

    ##############################################

    def __repr__(self) -> str:
        return self._value

    ##############################################

    # @classmethod
    # def format(cls, value) -> str:
    #     return f'{value}'

    ##############################################

    def to_json(self) -> dict:
        if self._longitude:
            return {'longitude': self._longitude, 'latitude': self._latidude}
        else:
            return self._value

####################################################################################################

class Delay:

    ##############################################

    def __init__(self, hours: int=0, minutes: int=0) -> None:
        self._minutes = int(hours * 60 + minutes)

    ##############################################

    @property
    def minutes(self) -> int:
        return self._minutes

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
        (('coordonnées zone départ', 'coordonnées ZD'), 'coordinate', Coordinate),
        ('date', 'date', str),   # to datetime later
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
        ('heure', 'hour', str),     # to datetime later
        (('inclinaison', 'inclinaison échelle'), 'inclination', Inclination),
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

    ##############################################

    @property
    def week(self) -> int:
        return self.date.isocalendar().week

    ##############################################

    def to_json(self) -> dict:
        return self.__dict__

####################################################################################################

class AccidentSheetContextManager:

    ##############################################

    def __init__(self, sheet: 'AccidentSheet') -> None:
        self._column_map = [Accident._MAP[_] for _ in sheet.column_titles]

    ##############################################

    def __enter__(self):
        return self

    ##############################################

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    ##############################################

    def convert(self, values: list) -> 'Accident':
        kwargs = {name: None for name, cls in Accident._MAP.values()}
        for i, value in enumerate(values):
            attribute, cls = self._column_map[i]
            if isinstance(value, str):
                value = value.strip()
                if not value:
                    value = None
            if value is not None:
                if issubclass(cls, MappedEnum):
                    value = cls.translate(value)
                elif cls is bool:
                    value = fr_to_bool(value)
                else:
                    value = cls(value)
            kwargs[attribute] = value

        date = kwargs['date']
        hour = kwargs['hour']
        if date:
            date = date.replace('-', '/')
            if hour:
                kwargs['date'] = datetime.datetime.strptime(f"{date} {hour}", '%d/%m/%Y %H:%M')
            else:
                kwargs['date'] = datetime.datetime.strptime(date, '%d/%m/%Y')
            del kwargs['hour']

        rescue_delay = kwargs['rescue_delay']
        if rescue_delay:
            hours = int(rescue_delay)
            # Fixme: ok ???
            minutes = int((rescue_delay - hours) * 100)
            # datetime.timedelta
            kwargs['rescue_delay'] = Delay(hours=hours, minutes=minutes)

        # pprint(kwargs)
        return Accident(**kwargs)

####################################################################################################

class AccidentEncoder(json.JSONEncoder):
    def default(self, obj):
        match obj:
            case Coordinate():
                return obj.to_json()
            case datetime.datetime():
                return obj.isoformat()
            case Delay():
                return obj.minutes
            case Enum():
                return MappedEnum.to_json(obj)
            case Inclination():
                return str(obj)
            case _:
                return json.JSONEncoder.default(self, obj)

####################################################################################################

class Accidents:

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
    def append(self, item: Accident) -> None:
        match item:
            case Accident():
                self._items.append(item)
            case Accidents():
                self._items.extend(item)

    def __iadd__(self, item: Accident) -> 'Accidents':
        self.append(item)
        return self

    ##############################################

    def to_json(self) -> list:
        return [_.to_json() for _ in self]

    ##############################################

    def write_json(self, path: Path) -> None:
        with open(path, 'w') as fh:
            data = json.dumps(
                accidents.to_json(),
                cls=AccidentEncoder,
                indent=4,
                ensure_ascii=False,
                sort_keys=True,
            )
            fh.write(data)

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
        row = self._sheet.row(i)
        values = []
        for cell in row:
            if cell.ctype == 3:
                # _ = xlrd.xldate.xldate_as_datetime(cell.value, 0)
                _ = xlrd.xldate.xldate_as_tuple(cell.value, 0)
                if _[0]:
                    value = f'{_[2]}/{_[1]}/{_[0]}'
                else:
                    value = f'{_[3]}:{_[4]}'
            else:
                value = cell.value
            values.append(value)
        return values

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

    def to_accident_pre_2019(self) -> Accidents:
        accidents = Accidents()
        sheet = self[0]
        with AccidentSheetContextManager(sheet) as cm:
            for row in sheet:
                # Skip total line
                if row[0]:
                    accidents += cm.convert(row)
        return accidents

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
        accidents = Accidents()
        for path in xls_paths:
            book = AccidentBook(path)
            if book.start_year < 2019:
                print()
                print('='*100)
                print(book.start_year)
                accidents += book.to_accident_pre_2019()
        accidents.write_json('anena-accidents.json')

        # for sheet in book[0]:
            # print(sheet.name)
            # print(sheet.column_titles)
        # sheet = book[1]
        # for row in sheet:
        #     anena_victim = Victim.from_2019(row)
