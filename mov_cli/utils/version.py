from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Tuple, List, Dict

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
    logger.debug("Checking if plugins need updating...")

    for _, module_name in plugins.items():
        plugin = load_plugin(module_name)

        if plugin is None:
            continue

        plugin_version = plugin.version
        pypi_package_name = plugin.hook_data.get("package_name", None)

        if plugin_version is not None:
            logger.debug(
                f"The plugin '{module_name}' doesn't expose '__version__' in" \
                    "it's root module ('__init__.py') so it the update checker will skip it."
            )
            continue

        if pypi_package_name is None:
            logger.debug(
                f"Skipped update check for '{module_name}' as the plugin " \
                    "doesn't contain 'package_name' in it's hook data."
            )
            continue

        try:
            response = httpx.get(f"https://pypi.org/pypi/{pypi_package_name}/json")
        except httpx.HTTPError as e:
            logger.warning(f"Failed to check for update of the plugin '{module_name}'! Error: {e}")
            continue

        if response.status_code >= 400:
            logger.warning(f"Failed to check for update of the plugin '{module_name}'! Response: {response}")
            continue

        pypi_json = response.json()
        pypi_version: str = pypi_json["info"]["version"]

        if version.parse(pypi_version) > version.parse(plugin_version):
            plugins_with_updates.append(pypi_package_name)

    if not plugins_with_updates == []:
        return True, plugins_with_updates

    return False, []