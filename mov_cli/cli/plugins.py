from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Tuple, List, Dict, NoReturn

    from ..plugins import PluginHookData

from devgoldyutils import Colours

from ..plugins import load_plugin
from ..logger import mov_cli_logger

def get_plugins_data(plugins: Dict[str, str]) -> List[Tuple[str, str, PluginHookData]]:
    plugins_data: List[Tuple[str, str, PluginHookData]] = []

    for plugin_namespace, plugin_module_name in plugins.items():
        plugin = load_plugin(plugin_module_name)

        if plugin is None:
            continue

        plugin_data, _ = plugin

        if plugin_data is None:
            continue

        plugins_data.append(
            (plugin_namespace, plugin_module_name, plugin_data)
        )

    return plugins_data

def show_all_plugins(plugins: Dict[str, str]) -> None:

    for plugin_namespace, plugin_module_name, plugin_hook_data in get_plugins_data(plugins):
        # TODO: Have 'get_plugins_data' return plugin module so we shouldn't have to load the plugin twice.
        plugin = load_plugin(plugin_module_name)

        if plugin is not None:
            plugin_module = plugin[1]

            plugin_version = getattr(plugin_module, "__version__", "N/A")

            print(f"- {Colours.PURPLE.apply(plugin_module_name)} ({plugin_namespace}) [{Colours.GREY.apply(plugin_version)}]")

            for scraper_name in plugin_hook_data["scrapers"]:
                if scraper_name == "DEFAULT":
                    continue

                print(f"  - {Colours.PINK_GREY.apply(scraper_name)}")

def handle_internal_plugin_error(e: Exception) -> NoReturn:
    mov_cli_logger.critical(
        "An error occurred inside a plugin. This is MOST LIKELY not a mov-cli error, " \
            f"make sure your plugins are up to date and ONLY report this to the plugin! \nError: {e}"
    )

    raise e