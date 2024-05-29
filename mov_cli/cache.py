from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, Any, Optional, TypeVar, TypedDict

    from io import TextIOWrapper

    from .utils.platform import SUPPORTED_PLATFORMS

    T = TypeVar("T", Any)

    class OsakaCacheData(TypedDict):
        value: Any
        timestamp: float

import json
from datetime import datetime
from devgoldyutils import LoggerAdapter, Colours

from .logger import mov_cli_logger
from .utils import get_temp_directory

__all__ = (
    "Cache",
)

logger = LoggerAdapter(
    mov_cli_logger, prefix = Colours.BLUE.apply("Cache")
)

class Cache():
    def __init__(self, platform: SUPPORTED_PLATFORMS) -> None:
        temp_dir = get_temp_directory(platform)

        self._basic_cache_file_path = temp_dir.joinpath("osaka_cache") # ◔_◔ https://static.wikia.nocookie.net/parody/images/f/fd/Osaka.png/revision/latest

        super().__init__()

    def get_cache(self, id: str) -> Optional[Any]:
        logger.debug(f"Getting '{id}' cache...")

        data: Dict[str, OsakaCacheData] = {}

        with self.__get_cache_file("r") as file:
            data = json.load(file)

        return data.get(id, {}).get("value")

    def set_cache(self, id: str, value: T, seconds_until_expired: int) -> T:
        logger.debug(f"Setting '{id}' cache...")

        json_data = {}

        with self.__get_cache_file("r") as file:
            json_data = json.load(file)

        with self.__get_cache_file("w") as file:
            timestamp = datetime.now().timestamp() + seconds_until_expired

            data = {
                **json_data, 
                **{
                    id: {
                        "value": value,
                        "expiring_date": timestamp
                    }
                }
            }

            json.dump(data, file)

        return value

    def clear_cache(self, id: str) -> None:
        logger.debug(f"Removing '{id}' cache...")

        json_data = {}

        with self.__get_cache_file("r") as file:
            json_data: Dict[str, OsakaCacheData] = json.load(file)

        with self.__get_cache_file("w") as file:
            json_data.pop(id)
            json.dump(json_data, file)

        return None

    def clear_all_cache(self) -> None:
        logger.info("Deleting basic cache file...")
        self._basic_cache_file_path.unlink(True)

    def __get_cache_file(self, mode: str) -> TextIOWrapper:

        if not self._basic_cache_file_path.exists():
            logger.debug("Cache file doesn't exist, creating one...")

            with self._basic_cache_file_path.open("w") as file:
                file.write("{}")

        return self._basic_cache_file_path.open(mode, encoding = "utf+8")