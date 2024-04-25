from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Type, Optional, Tuple, List, Dict

    from ..media import Metadata, Media
    from ..http_client import HTTPClient
    from ..config import Config, ScrapersConfigT
    from ..utils.episode_selector import EpisodeSelector

    from ..plugins import PluginHookData
    from ..scraper import Scraper, ScraperOptionsT

from devgoldyutils import Colours

from .ui import prompt
from .plugins import get_plugins_data, handle_internal_plugin_error

from ..logger import mov_cli_logger

def scrape(choice: Metadata, episode: EpisodeSelector, scraper: Scraper) -> Media:
    mov_cli_logger.info(f"Scrapping media for '{Colours.CLAY.apply(choice.title)}'...")

    try:
        media = scraper.scrape(choice, episode)
    except Exception as e:
        handle_internal_plugin_error(e)

    return media

def use_scraper(
    selected_scraper: Tuple[str, Type[Scraper], ScraperOptionsT], 
    config: Config, 
    http_client: HTTPClient
) -> Scraper:
    scraper_name, scraper_class, scraper_options = selected_scraper

    mov_cli_logger.info(f"Using '{Colours.BLUE.apply(scraper_name)}' scraper...")

    try:
        chosen_scraper = scraper_class(config, http_client, scraper_options)
    except Exception as e:
        handle_internal_plugin_error(e)

    return chosen_scraper

def select_scraper(plugins: Dict[str, str], scrapers: ScrapersConfigT, fzf_enabled: bool, default_scraper: Optional[str] = None) -> Optional[Tuple[str, Type[Scraper], ScraperOptionsT]]:
    plugins_data = get_plugins_data(plugins)

    if default_scraper is not None:
        scraper_name, scraper_or_available_scrapers, scraper_options = get_scraper(default_scraper, plugins_data, scrapers)

        if scraper_name is None:
            mov_cli_logger.error(
                f"Could not find a scraper by the id '{default_scraper}'! Are you sure the plugin is installed and in your config? " \
                    "Read the wiki for more on that: 'https://github.com/mov-cli/mov-cli/wiki#plugins'." \
                    f"\n\n  {Colours.GREEN}Available Scrapers{Colours.RESET} -> {scraper_or_available_scrapers}"
            )

            return None

        return scraper_name, scraper_or_available_scrapers, scraper_options

    chosen_plugin = prompt(
        "Select a plugin", 
        choices = plugins_data, 
        display = lambda x: f"{Colours.ORANGE.apply(x[0])} [{Colours.PINK_GREY.apply(x[1])}]", 
        fzf_enabled = fzf_enabled
    )

    if chosen_plugin is not None:
        plugin_namespace, _, plugin_data, plugin = chosen_plugin

        chosen_scraper = prompt(
            "Select a scraper", 
            choices = [scraper for scraper in plugin_data["scrapers"].items()], 
            display = lambda x: Colours.BLUE.apply(x[0].lower()), 
            fzf_enabled = fzf_enabled
        )

        if chosen_scraper is None:
            return None

        scraper_name, scraper = chosen_scraper

        return f"{plugin_namespace}.{scraper_name}".lower(), scraper, {}

    return None

def steal_scraper_args(query: List[str]) -> ScraperOptionsT:
    scrape_arguments = [x for x in query if "--" in x]

    mov_cli_logger.debug(f"Scraper args picked up on --> {scrape_arguments}")

    for scrape_arg in scrape_arguments:
        query.remove(scrape_arg)

    return dict(
        [(x.replace("--", "").replace("-", "_"), True) for x in scrape_arguments]
    )

def get_scraper(scraper_id: str, plugins_data: List[Tuple[str, str, PluginHookData]], user_defined_scrapers: ScrapersConfigT) -> Tuple[str, Type[Scraper] | Tuple[None, List[str]], ScraperOptionsT]:
    scraper_options = {}
    available_scrapers = []

    # scraper namespace override.
    for scraper_namespace, scraper_data in user_defined_scrapers.items():

        if scraper_id.lower() == scraper_namespace.lower():
            mov_cli_logger.debug(f"Using the scraper overridden namespace '{scraper_namespace}'...")
            scraper_id = scraper_data["namespace"]
            scraper_options = scraper_data["options"]

    for plugin_namespace, _, plugin_hook_data, plugin in plugins_data:
        plugin_scrapers = plugin_hook_data["scrapers"]

        if scraper_id.lower() == plugin_namespace.lower() and "DEFAULT" in plugin_scrapers:
            return f"{plugin_namespace}.DEFAULT", plugin_scrapers["DEFAULT"], scraper_options

        for scraper_name, scraper in plugin_scrapers.items():
            id = f"{plugin_namespace}.{scraper_name}".lower()

            available_scrapers.append(id)

            if scraper_id.lower() == id:
                return id, scraper, scraper_options

    return None, available_scrapers, scraper_options