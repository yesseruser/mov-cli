from __future__ import annotations
from typing import TYPE_CHECKING, TypedDict, final
from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .players import Player
    from typing import Dict, Literal, Any, Optional

    SupportedParsersT = Literal["lxml", "html.parser"]

    @final
    class ScraperData(TypedDict):
        namespace: str
        options: Dict[str, str | bool]

    ScrapersConfigT = Dict[Literal["default"], str] | Dict[str, ScraperData]

import os
import toml
import shutil
from pathlib import Path
from decouple import AutoConfig
from importlib.util import find_spec
from devgoldyutils import LoggerAdapter

from . import players, utils
from .logger import mov_cli_logger
from .utils import get_appdata_directory
from .media import Quality

__all__ = ("Config",)

@final
class ConfigUIData(TypedDict):
    fzf: bool

@final
class ConfigHTTPData(TypedDict):
    headers: Dict[str, str]

@final
class ConfigDownloadsData(TypedDict):
    save_path: str
    yt_dlp: bool

@final
class ConfigQualityData(TypedDict):
    resolution: int

@final
class ConfigData(TypedDict):
    version: int
    debug: bool
    player: str
    editor: str
    parser: SupportedParsersT
    skip_update_checker: bool
    hide_ip: bool
    ui: ConfigUIData
    http: ConfigHTTPData
    downloads: ConfigDownloadsData
    scrapers: ScrapersConfigT | Dict[str, str]
    plugins: Dict[str, str]
    quality: ConfigQualityData | str

HttpHeadersData = TypedDict(
    "HttpHeadersData", 
    {
        "User-Agent": NotRequired[str],
        "Accept-Language": NotRequired[str],
        "Accept": NotRequired[str]
    }
)

logger = LoggerAdapter(mov_cli_logger, prefix = "Config")

class Config():
    """Class that wraps the mov-cli configuration file. Mostly used under the CLI interface."""
    def __init__(self, override_config: ConfigData = None, config_path: Path = None) -> None:
        self.config_path = config_path
        self._env_path = self.__get_env_file()

        self.data: ConfigData = {}

        if override_config is None:
            self.config_path = self.__get_config_file()

            try:
                self.data = toml.load(self.config_path).get("mov-cli", {})
            except toml.decoder.TomlDecodeError as e:
                logger.critical(
                    "Failed to read config.toml! Please check you haven't made any mistakes in the config." \
                        f"All values will fallback to default. \nError: {e}"
                )

        else:
            self.data = override_config

    @property
    def version(self) -> int:
        return self.data.get("version", 1)

    @property
    def player(self) -> Player:
        """Returns the player class that was configured in the config. Defaults to MPV."""
        value = self.data.get("player", "mpv")

        platform = utils.what_platform()

        if value.lower() == "mpv":
            return players.MPV(platform, self)
        elif value.lower() == "vlc":
            return players.VLC(platform, self)
        elif value.lower() == "syncplay":
            return players.SyncPlay(platform, self)
        elif value.lower() == "iina":
            return players.IINA(platform, self)

        return players.CustomPlayer(value)

    @property
    def plugins(self) -> Dict[str, str]:
        return self.data.get("plugins", {"test": "mov-cli-test"})

    @property
    def scrapers(self) -> ScrapersConfigT:
        scrapers = self.data.get("scrapers", {})

        consistent_scrapers: Dict[str, ScraperData] = {}

        for scraper, plugin_namespace_or_dict in scrapers.items():

            if scraper == "default":
                consistent_scrapers["default"] = plugin_namespace_or_dict

            elif isinstance(plugin_namespace_or_dict, str):
                consistent_scrapers[scraper] = {"namespace": plugin_namespace_or_dict, "options": {}}

            else:
                dict = plugin_namespace_or_dict
                consistent_scrapers[scraper] = {
                    "namespace": dict["namespace"], 
                    "options": dict["options"]
                }

        return consistent_scrapers

    @property
    def editor(self) -> Optional[str]:
        """Returns the editor that should be opened while editing."""
        return self.data.get("editor", None)

    @property
    def skip_update_checker(self) -> bool:
        return self.data.get("skip_update_checker", False)
    
    @property
    def hide_ip(self) -> bool:
        return self.data.get("hide_ip", True)

    @property
    def default_scraper(self) -> Optional[str]:
        """Returns the scraper that should be used to scrape by default."""
        return self.data.get("scrapers", {}).get("default", None)

    @property
    def fzf_enabled(self) -> bool:
        """Returns whether fzf is allowed to be used. Defaults to True of fzf is available."""
        return self.data.get("ui", {}).get("fzf", True if shutil.which("fzf") is not None else False)

    @property
    def parser(self) -> SupportedParsersT | Any:
        """Returns the parser type configured by the user else it just returns the default."""
        default_parser = "lxml" if find_spec("lxml") else "html.parser"
        return self.data.get("parser", default_parser)

    @property
    def download_location(self) -> str:
        """Returns download location. Defaults to current working directory."""
        return self.data.get("downloads", {}).get("save_path", os.getcwd())

    @property
    def use_yt_dlp(self) -> bool:
        """Returns if yt-dlp should be used. Defaults to True."""
        return self.data.get("downloads", {}).get("yt_dlp", True)

    @property
    def debug(self) -> bool:
        """Returns whether debug should be enabled or not."""
        return self.data.get("debug", False)

    @property
    def proxy(self) -> dict | None:
        """Returns proxy data. Defaults to None"""
        proxy_config = self.data.get("proxy")

        if proxy_config is not None:
            proxy = None

            username = proxy_config.get("username")
            password = proxy_config.get("password")

            scheme = proxy_config.get("scheme")
            ip = proxy_config.get("ip")
            port = proxy_config.get("port")

            if username and password:
                proxy = f"{scheme}://{username}:{password}@{ip}:{port}"
            else:
                proxy = f"{scheme}://{ip}:{port}"

            return {"all://": proxy}
        else:
            return None

    @property
    def http_headers(self) -> HttpHeadersData:
        """Returns http headers."""
        default_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        }

        return self.data.get("http", {}).get("headers", default_headers)

    @property
    def resolution(self) -> Quality:
        resolution_pixel = None
        quality_config = self.data.get("quality", {})

        if isinstance(quality_config, str):

            for quality_format, quality in Quality.__members__.items():

                if quality_format.startswith("_"):
                    quality_format = quality_format[1:]

                if quality_config.upper() == quality_format:
                    return quality

            return Quality.AUTO

        resolution_pixel = quality_config.get("resolution")

        if resolution_pixel is None or resolution_pixel not in Quality._value2member_map_:
            return Quality.AUTO

        return Quality(resolution_pixel)

    def get_env_config(self) -> AutoConfig:
        """Returns python decouple config object for mov-cli's appdata .env file."""
        return AutoConfig(self._env_path)

    def __get_config_file(self) -> Path:
        """Function that returns the path to the config file with multi platform support."""
        platform = utils.what_platform()

        appdata_folder = get_appdata_directory(platform)

        config_path = appdata_folder.joinpath("config.toml")

        if not config_path.exists():
            logger.debug("The 'config.toml' file doesn't exist so we're creating it...")
            config_file = open(config_path, "w")

            template_config_path = f"{Path(os.path.split(__file__)[0])}{os.sep}config.template.toml"

            with open(template_config_path, "r") as config_template:
                config_file.write(config_template.read())

            config_file.close()
            logger.info(f"Config created at '{config_path}'.")

        return config_path

    def __get_env_file(self) -> Path:
        """Function that returns the path to the mov-cli .env file."""
        platform = utils.what_platform()

        appdata_folder = get_appdata_directory(platform)

        env_file_path = appdata_folder.joinpath(".env")

        if not env_file_path.exists():
            logger.debug("The 'config.toml' file doesn't exist so we're creating it...")
            open(env_file_path, "w").close()
            logger.info(f".env file created at '{env_file_path}'.")

        return env_file_path