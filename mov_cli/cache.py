from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, Any, Optional, TypeVar, TypedDict

    from io import TextIOWrapper

    from .utils.platform import SUPPORTED_PLATFORMS

    T = TypeVar("T", Any)

    class BasicCacheData(TypedDict):
        value: Any
        expiring_date: Optional[float]

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
    """An API for caching text based data on mov-cli cross platform respectively."""
    def __init__(self, platform: SUPPORTED_PLATFORMS) -> None:
        temp_dir = get_temp_directory(platform)

        self._basic_cache_file_path = temp_dir.joinpath("osaka_cache") # ◔_◔ https://static.wikia.nocookie.net/parody/images/f/fd/Osaka.png/revision/latest

        super().__init__()

    def get_cache(self, id: str) -> Optional[Any]:
        logger.debug(f"Getting '{id}' cache...")

        data: Dict[str, BasicCacheData] = {}

        with self.__get_cache_file("r") as file:
            data = json.load(file)

        basic_cache = data.get(id)

        if basic_cache is None:
            return None

        expiring_data = basic_cache["expiring_date"]

        if expiring_data is not None and datetime.now().timestamp() > expiring_data:
            self.clear_cache(id)
            return None

        return data.get(id, {}).get("value")

    def set_cache(self, id: str, value: T, seconds_until_expired: Optional[int] = None) -> T:
        logger.debug(f"Setting '{id}' cache...")

        json_data = {}

        with self.__get_cache_file("r") as file:
            json_data: Dict[str, BasicCacheData] = json.load(file)

        with self.__get_cache_file("w") as file:
            timestamp = None

            if seconds_until_expired is not None:
                timestamp = datetime.now().timestamp() + float(seconds_until_expired)

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
            json_data: Dict[str, BasicCacheData] = json.load(file)

        with self.__get_cache_file("w") as file:
            json_data.pop(id)
            json.dump(json_data, file)

        return None

    def clear_all_cache(self) -> None:
        logger.info(f"Deleting basic cache file ({self._basic_cache_file_path.name})...")
        self._basic_cache_file_path.unlink(True)

    def __get_cache_file(self, mode: str) -> TextIOWrapper:

        if not self._basic_cache_file_path.exists():
            logger.debug("Cache file doesn't exist, creating one...")

            with self._basic_cache_file_path.open("w") as file:
                file.write("{}")

        return self._basic_cache_file_path.open(mode, encoding = "utf+8")