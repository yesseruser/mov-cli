from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Type, Optional, Tuple, List, Dict

    from ..config import Config
    from ..media import Metadata, Media
    from ..http_client import HTTPClient
    from ..utils.episode_selector import EpisodeSelector

    from .plugins import PluginsDataT
    from ..scraper import Scraper, ScraperOptionsT

from devgoldyutils import Colours

from .ui import prompt
from .plugins import get_plugins_data, handle_internal_plugin_error

from ..utils import what_platform
from ..logger import mov_cli_logger

def scrape(choice: Metadata, episode: EpisodeSelector, scraper: Scraper) -> Media:
    mov_cli_logger.info(f"Scrapping media for '{Colours.CLAY.apply(choice.title)}'...")

    try:
        media = scraper.scrape(choice, episode)
    except Exception as e:
        handle_internal_plugin_error(e)

    return media

def use_scraper(
    selected_scraper: Tuple[str, Type[Scraper]], 
    config: Config, 
    http_client: HTTPClient,
    scraper_options: ScraperOptionsT
) -> Scraper:
    scraper_name, scraper_class = selected_scraper

    mov_cli_logger.info(f"Using '{Colours.BLUE.apply(scraper_name)}' scraper...")

    try:
        chosen_scraper = scraper_class(config, http_client, scraper_options)
    except Exception as e:
        handle_internal_plugin_error(e)

    return chosen_scraper

def select_scraper(plugins: Dict[str, str], fzf_enabled: bool, default_scraper: Optional[str] = None) -> Optional[Tuple[str, Type[Scraper]]]:
    plugins_data = get_plugins_data(plugins)

    if default_scraper is not None:
        scraper_name, scraper_or_available_scrapers = get_scraper(default_scraper, plugins_data)

        if scraper_name is None:
            mov_cli_logger.error(
                f"Could not find a scraper by the id '{default_scraper}'! Are you sure the plugin is installed and in your config? " \
                    "Read the wiki for more on that: 'https://github.com/mov-cli/mov-cli/wiki#plugins'." \
                    f"\n\n  {Colours.GREEN}Available Scrapers{Colours.RESET} -> {scraper_or_available_scrapers}"
            )

            return None

        return scraper_name, scraper_or_available_scrapers

    chosen_plugin = prompt(
        "Select a plugin", 
        choices = plugins_data, 
        display = lambda x: f"{Colours.ORANGE.apply(x[0])} [{Colours.PINK_GREY.apply(x[1])}]", 
        fzf_enabled = fzf_enabled
    )

    if chosen_plugin is not None:
        plugin_namespace, _, plugin = chosen_plugin

        chosen_scraper = prompt(
            "Select a scraper", 
            choices = [scraper for scraper in plugin.scrapers], 
            display = lambda x: Colours.BLUE.apply(x[0].lower()), 
            fzf_enabled = fzf_enabled
        )

        if chosen_scraper is None:
            return None

        scraper_name, scraper = chosen_scraper

        return f"{plugin_namespace}.{scraper_name}".lower(), scraper

    return None

def steal_scraper_args(query: List[str]) -> ScraperOptionsT:
    args_to_kidnap: List[str] = []
    arg_values_to_kidnap: List[str] = []

    scraper_options_args: List[Tuple[str, str | bool]] = []

    for index, arg in enumerate(query):

        if arg.startswith("--"):
            arg_value = True

            try:
                arg_value_maybe = query[index + 1]

                if not arg_value_maybe.startswith("--"):
                    arg_value = arg_value_maybe

                    arg_values_to_kidnap.append(arg_value)

            except IndexError as e:
                mov_cli_logger.debug(
                    f"No scraper option argument value was found after '{arg}' so we'll assume this argument is a flag. \nError: {e}"
                )

            args_to_kidnap.append(arg)
            scraper_options_args.append((arg.replace("--", "").replace("-", "_"), arg_value))

    # KIDNAP THEM ARGS!!!!!
    for arg_or_arg_value in args_to_kidnap + arg_values_to_kidnap:
        query.remove(arg_or_arg_value)

    mov_cli_logger.debug(f"Scraper args picked up on --> {scraper_options_args}")

    return dict(scraper_options_args)

def get_scraper(scraper_id: str, plugins_data: PluginsDataT) -> Tuple[str, Type[Scraper] | Tuple[None, List[str]]]:
    available_scrapers = []

    platform = what_platform().upper()

    for plugin_namespace, _, plugin in plugins_data:
        scrapers = plugin.hook_data["scrapers"]

        if scraper_id.lower() == plugin_namespace.lower() and f"{platform}.DEFAULT" in scrapers:
            return f"{plugin_namespace}.{platform}.DEFAULT", scrapers[f"{platform}.DEFAULT"]

        elif scraper_id.lower() == plugin_namespace.lower() and "DEFAULT" in scrapers:
            return f"{plugin_namespace}.DEFAULT", scrapers["DEFAULT"]

        for scraper_name, scraper in scrapers.items():
            id = f"{plugin_namespace}.{scraper_name}".lower()

            available_scrapers.append(id)

            if scraper_id.lower() == id:
                return id, scraper

    return None, available_scrapers