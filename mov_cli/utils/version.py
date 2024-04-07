from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Tuple, List, Optional, Dict

import httpx
from packaging import version
from devgoldyutils import LoggerAdapter, Colours

import mov_cli
from ..plugins import load_plugin
from ..logger import mov_cli_logger

__all__ = (
    "update_available", 
    "plugin_update_available"
)

logger = LoggerAdapter(mov_cli_logger, prefix = Colours.GREEN.apply("version"))

logger = LoggerAdapter(mov_cli_logger, prefix = Colours.GREEN.apply("version"))

def update_available() -> bool:
    logger.debug("Checking if mov-cli needs updating...")

    update_fail_msg = "Failed to check for mov-cli update!"

    try:
        response = httpx.get("https://pypi.org/pypi/mov-cli/json")
    except httpx.HTTPError as e:
        logger.warning(update_fail_msg + f" Error: {e}")
        return False

    if response.status_code >= 400:
        logger.warning(update_fail_msg + f" Response: {response}")
        return False

    pypi_json = response.json()
    pypi_version: str = pypi_json["info"]["version"]

    if version.parse(pypi_version) > version.parse(mov_cli.__version__):
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