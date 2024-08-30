from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, Callable, Dict

    from ..media import Metadata
    from ..plugins import Plugin
    from ..scraper import Scraper
    from ..utils.platform import SUPPORTED_PLATFORMS

import re
from devgoldyutils import Colours

from .ui import prompt
from .scraper import use_scraper
from .auto_select import auto_select_choice
from .plugins import handle_internal_plugin_error, get_plugins_data

from ..cache import Cache
from ..logger import mov_cli_logger

def cache_image_for_preview(cache: Cache) -> Callable[[Metadata], Metadata]:
    ansi_remover = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])') # Remove colours

    def before_display_callable(metadata: Metadata) -> Metadata:
        cache.set_cache(ansi_remover.sub("", metadata.display_name), metadata.image_url)

        return metadata

    return before_display_callable

def search(
    query: str,
    auto_select: Optional[int],
    scraper: Scraper,
    scraper_namespace: str,
    platform: SUPPORTED_PLATFORMS,
    auto_try_next_scraper: bool,
    fzf_enabled: bool,
    preview: bool,
    plugins: Dict[str, str],
    limit: Optional[int]
) -> Optional[Metadata]:
    choice = None

    cache = Cache(platform, section = "image_urls")

    mov_cli_logger.info(f"Searching for '{Colours.ORANGE.apply(query)}'...")

    try:
        search_results = scraper.search(query, limit)
    except Exception as e:
        handle_internal_plugin_error(e)

    if auto_select is not None:
        choice = auto_select_choice((choice for choice in search_results), auto_select)
    else:
        choice = prompt(
            "Choose Result", 
            choices = (choice for choice in search_results), 
            display = lambda x: x.display_name, 
            fzf_enabled = fzf_enabled,
            before_display = cache_image_for_preview(cache),
            preview = "mov-cli-dev preview image -- {}" if preview else None
        )

    cache.clear_all_cache()

    if choice is None and auto_try_next_scraper:
        mov_cli_logger.warning(
            f"Query not found with '{Colours.BLUE.apply(scraper_namespace)}', automatically searching with the next scraper in that plugin..."
        )

        return search_with_next_scraper(
            query = query,
            auto_select = auto_select,
            current_scraper = scraper,
            current_scraper_namespace = scraper_namespace,
            platform = platform,
            fzf_enabled = fzf_enabled,
            preview = preview,
            plugins = plugins,
            limit = limit
        )

    return choice

def search_with_next_scraper(
    query: str,
    auto_select: Optional[int],
    current_scraper: Scraper,
    current_scraper_namespace: str,
    platform: SUPPORTED_PLATFORMS,
    fzf_enabled: bool,
    preview: bool,
    plugins: Dict[str, str],
    limit: Optional[int]
) -> Optional[Metadata]:
    current_plugin_namespace, current_scraper_namespace = current_scraper_namespace.split(".")

    current_plugin: Plugin # It should get bound. Like it's impossible for it to not. 💀

    for plugin_namespace, _, plugin in get_plugins_data(plugins):

        if plugin_namespace == current_plugin_namespace:
            current_plugin = plugin
            break

    # Replace the current scraper namespace with actual scraper 
    # namespace if the namespace we got was the default scraper namespace.
    if current_scraper_namespace.endswith("DEFAULT"):

        for plugin_scraper_namespace, plugin_scraper in current_plugin.scrapers:

            if plugin_scraper == current_plugin.hook_data["scrapers"][current_scraper_namespace]:
                current_scraper_namespace = plugin_scraper_namespace
                break

    print(">", current_scraper_namespace)

    next_plugin_scraper_class = None
    next_plugin_scraper_namespace = None

    for plugin_namespace, _, plugin in get_plugins_data(plugins):

        if plugin_namespace == current_plugin_namespace:

            # We get the next scraper by finding the current chosen scraper and returning 
            # the one after that. If none exist then that is the last scraper so we just continue.
            current_chosen_scraper_found = False

            plugin_scrapers_amount = len(plugin.scrapers)

            for index, (plugin_scraper_namespace, plugin_scraper_class) in enumerate(plugin.scrapers):

                if plugin_scraper_namespace == current_scraper_namespace:

                    # If we are on the last scraper the next scraper should 
                    # be None to indicate that there's no more scrapers after.
                    if plugin_scrapers_amount - 1 == index:
                        next_plugin_scraper = None
                        break

                    current_chosen_scraper_found = True

                if not current_chosen_scraper_found:
                    continue

                next_plugin_scraper_class = plugin_scraper_class
                next_plugin_scraper_namespace = f"{plugin_namespace}.{plugin_scraper_namespace}"
                break

            break

    if next_plugin_scraper_class is None:
        return None

    mov_cli_logger.info(f"Switched to the '{Colours.BLUE.apply(next_plugin_scraper_namespace)}' scraper.")

    next_plugin_scraper = use_scraper(
        selected_scraper = (next_plugin_scraper_namespace, next_plugin_scraper_class, current_scraper.options),
        config = current_scraper.config,
        http_client = current_scraper.http_client
    )

    return search(
        query,
        auto_select,
        next_plugin_scraper,
        next_plugin_scraper_namespace,
        platform,
        True,
        fzf_enabled,
        preview,
        plugins,
        limit
    )