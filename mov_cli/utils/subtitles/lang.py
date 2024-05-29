import json
from pathlib import Path
import os

__all__ = ("Lang",)

iso_file = Path(os.path.split(__file__)[0]).joinpath("iso_639.json")

with open(iso_file, "r", encoding="utf-8") as f:
    iso = json.loads(
        f.read()
    )

class Lang():
    def __init__(self, alpha2: str):
        self.__json_data = iso.get(alpha2, {})

    @property
    def name(self):
        return self.__json_data.get("name")
    
    @property
    def nativeName(self):
        return self.__json_data.get("nativeName")

    @property
    def iso639_1(self):
        return self.__json_data.get("639-1")
    
    @property
    def iso639_2(self):
        return self.__json_data.get("639-2")