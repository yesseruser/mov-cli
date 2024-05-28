from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, Any, Optional, TypeVar

    from io import TextIOWrapper

    from .utils.platform import SUPPORTED_PLATFORMS

    T = TypeVar("T", Any)

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

        self._cache_file = temp_dir.joinpath("osaka_cache") # ◔_◔ https://static.wikia.nocookie.net/parody/images/f/fd/Osaka.png/revision/latest

        super().__init__()

    def get_cache(self, cache_name: str) -> Optional[Any]:
        logger.debug(f"Getting '{cache_name}' cache...")

        data: Dict[str, Any] = {}

        with self.__get_cache_file("r") as file:
            data = json.load(file)

        return data.get(cache_name)["value"]

    def set_cache(self, cache_name: str, value: T, seconds_until_expired: int) -> T:
        logger.debug(f"Setting '{cache_name}' cache...")

        json_data = {}

        with self.__get_cache_file("r") as file:
            json_data = json.load(file)

        with self.__get_cache_file("w") as file:
            timestamp = datetime.now().timestamp() + seconds_until_expired

            data = {
                **json_data, 
                **{
                    cache_name: {
                        "value": value,
                        "expiring_date": timestamp
                    }
                }
            }

            json.dump(data, file)

        return value

    def clear_cache(self) -> None:
        logger.info("Deleting cache file...")
        self._cache_file.unlink(True)

    def __get_cache_file(self, mode: str) -> TextIOWrapper:

        if not self._cache_file.exists():
            logger.debug("Cache file doesn't exist, creating one...")

            with self._cache_file.open("w") as file:
                file.write("{}")

        return self._cache_file.open(mode, encoding = "utf+8")