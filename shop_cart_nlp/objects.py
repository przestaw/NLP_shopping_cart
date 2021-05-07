from dataclasses import dataclass, field

from dataclasses_json import dataclass_json


# Note : https://pypi.org/project/dataclasses-json/


@dataclass_json
@dataclass
class Product:
    name: str
    description: str
    prod_id: int = field(default=None)


@dataclass
class Stem:
    stem_id: int  # TODO may br None [unknown/not inserted]
    value: str


@dataclass
class ProdStem:
    prod_id: int
    stem_id: int
