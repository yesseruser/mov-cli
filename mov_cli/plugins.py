"""
Module containing mov-cli plugin related stuff.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from types import ModuleType
    from typing import Optional, Dict, Literal, List, Tuple

    from .scraper import Scraper

import importlib
from dataclasses import dataclass
from devgoldyutils import LoggerAdapter

from .logger import mov_cli_logger

__all__ = (
    "load_plugin", 
    "PluginHookData", 
    "Plugin"
)

logger = LoggerAdapter(mov_cli_logger, prefix = "Plugins")

class PluginHookData(TypedDict):
    version: int
    """The version of the plugin hook to use. Version 1 is latest currently."""
    package_name: str
    """The name of the pypi package. This is required for the plugin update notifier to work."""
    scrapers: Dict[str, Scraper] | Dict[Literal["DEFAULT"], Scraper]

@dataclass
class Plugin:
    module: ModuleType
    hook_data: PluginHookData

    @property
    def scrapers(self) -> List[Tuple[str, Scraper]]:
        non_default_scrapers = []

        for scraper_namespace, scraper_class in self.hook_data["scrapers"].items():

            if scraper_namespace.endswith("DEFAULT"):
                continue

            non_default_scrapers.append((scraper_namespace, scraper_class))

        return non_default_scrapers

def load_plugin(module_name: str) -> Optional[Plugin]:
    try:
        plugin_module = importlib.import_module(module_name.replace("-", "_"))
    except ModuleNotFoundError as e:
        logger.error(f"Failed to import a plugin from the module '{module_name}'! Error --> {e}")
        return None

    plugin_data: PluginHookData = getattr(plugin_module, "plugin", None)

    if plugin_data is None:
        logger.warning(f"Failed to load the plugin '{module_name}'! It doesn't contain a plugin hook!")
        return None

    return Plugin(
        module = plugin_module, 
        hook_data = plugin_data
    )