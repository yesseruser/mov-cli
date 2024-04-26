from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Tuple, List, Dict, NoReturn

    from ..plugins import Plugin
    PluginsDataT = List[Tuple[str, str, Plugin]]

from devgoldyutils import Colours

from ..plugins import load_plugin
from ..logger import mov_cli_logger

def get_plugins_data(plugins: Dict[str, str]) -> PluginsDataT:
    plugins_data: PluginsDataT = []

    for plugin_namespace, plugin_module_name in plugins.items():
        plugin = load_plugin(plugin_module_name)

        if plugin is None:
            continue

        plugins_data.append(
            (plugin_namespace, plugin_module_name, plugin)
        )

    return plugins_data

def show_all_plugins(plugins: Dict[str, str]) -> None:

    for plugin_namespace, plugin_module_name, plugin in get_plugins_data(plugins):

        if plugin is not None:
            plugin_version = getattr(plugin.module, "__version__", "N/A")

            print(f"- {Colours.PURPLE.apply(plugin_module_name)} ({plugin_namespace}) [{Colours.BLUE.apply(plugin_version)}]")

            for scraper_name in plugin.scrapers:
                print(f"  - {Colours.PINK_GREY.apply(scraper_name[0])}")

def handle_internal_plugin_error(e: Exception) -> NoReturn:
    mov_cli_logger.critical(
        "An error occurred inside a plugin. This is MOST LIKELY not a mov-cli error, " \
            f"make SURE mov-cli and your plugins are up to date. Also report this to the plugin, not mov-cli! \nError: {e}"
    )

    raise e