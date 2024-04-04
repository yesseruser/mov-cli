from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Tuple, List, Optional, Dict

import httpx
from devgoldyutils import LoggerAdapter, Colours

import mov_cli
from ..plugins import load_plugin
from ..logger import mov_cli_logger

__all__ = (
    "update_available", 
    "plugin_update_available"
)

logger = LoggerAdapter(mov_cli_logger, prefix = Colours.GREEN.apply("version"))

def update_available() -> bool:
    pypi = httpx.get("https://pypi.org/pypi/mov-cli/json").json()
    pypi_ver = pypi["info"]["version"]

    if pypi_ver > mov_cli.__version__:
        return True

    return False

def plugin_update_available(plugins: Dict[str, str]) -> Tuple[bool, List[str]]:
    plugins_with_updates: List[str] = []

    for _, module_name in plugins.items():
        plugin = load_plugin(module_name)

        if plugin is None:
            continue

        plugin_module = plugin[1]
        plugin_version: Optional[int] = getattr(plugin_module, "__version__", None)

        if plugin_version is None:
            continue

        logger.debug(f"Checking if the plugin '{module_name}' is up to date...")

        # NOTE: Welp, this would break for plugins not named consistently but I can't think of a solution rn and it's getting late 😴
        pypi_package_name = module_name.replace("_", "-")
        response = httpx.get(f"https://pypi.org/pypi/{pypi_package_name}/json")

        if response.status_code > 400:
            logger.warning(f"Failed to check pypi version of the plugin '{module_name}'!")
            continue

        pypi_json = response.json()
        pypi_version: int = pypi_json["info"]["version"]

        if pypi_version > plugin_version:
            plugins_with_updates.append(module_name)

    if not plugins_with_updates == []:
        return True, plugins_with_updates

    return False, []