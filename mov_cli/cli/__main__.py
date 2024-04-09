from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    ...

import typer
import logging
from devgoldyutils import Colours

from .play import play
from .search import search
from .episode import handle_episode
from .scraper import select_scraper, use_scraper, scrape, get_plugins_data
from .configuration import open_config_file, set_cli_config
from .utils import welcome_msg, steal_scraper_args

from ..config import Config
from ..download import Download
from ..logger import mov_cli_logger
from ..http_client import HTTPClient

__all__ = ("mov_cli",)

uwu_app = typer.Typer(pretty_exceptions_enable = False) # NOTE: goldy has an uwu complex.

def mov_cli(
    query: Optional[List[str]] = typer.Argument(None, help = "A film, tv show or anime you would like to Query."), 
    debug: Optional[bool] = typer.Option(None, help = "Enable extra logging details. Useful for bug reporting."), 
    player: Optional[str] = typer.Option(None, "--player", "-p", help = "Player you would like to stream with. E.g. mpv, vlc"), 
    scraper: Optional[str] = typer.Option(None, "--scraper", "-s", help = "Scraper you would like to scrape with. E.g. remote_stream, sflix"), 
    fzf: Optional[bool] = typer.Option(None, help = "Toggle fzf on/off for all user selection prompts."), 
    episode: Optional[str] = typer.Option(None, "--episode", "-ep", help = "Episode and season you wanna scrape. E.g. {episode}:{season} like -> 26:3"), 
    auto_select: Optional[int] = typer.Option(None, "--choice", "-c", help = "Auto select the search results. E.g. Setting it to 1 with query 'nyan cat' will pick " \
        "the first nyan cat video to show up in search results."
    ), 
    list_scrapers: Optional[str] = typer.Option(None, "--list-scrapers", "-ls", help = "Prints all scrapers available in the plugin"),


    version: bool = typer.Option(False, "--version", help = "Display what version mov-cli is currently on."), 
    edit: bool = typer.Option(False, "--edit", "-e", help = "Opens the mov-cli config with your respective editor."), 
    download: bool = typer.Option(False, "--download", "-d", help = "Downloads the media instead of playing."),
    list_plugins: bool = typer.Option(False, "--list-plugins", "-lp", help = "Prints all configured plugins."),
):
    config = Config()

    config = set_cli_config(
        config,
        debug = debug,
        player = player,
        scraper = scraper,
        fzf = fzf
    )

    if config.debug:
        mov_cli_logger.setLevel(logging.DEBUG)

    mov_cli_logger.debug(f"Config -> {config.data}")

    if edit:
        open_config_file(config)
        return None
    
    if list_plugins:
        string = "Configured Plugins:\r\n\n"

        plugins = []

        plugins_data = get_plugins_data(config.plugins)

        for plugin_namespace, _, plugin_hook_data in plugins_data:
            plugins.append(f"- {Colours.PINK_GREY}{plugin_namespace}{Colours.RESET}\n")
        
        if not plugins:
            mov_cli_logger.error("You don't have any plugins configured!")

            return None

        print(string + "\n".join(plugins))
        return None
    
    if list_scrapers is not None: # NOTE: This is the best way, i can come up with at 6 am.
        string = f"Scrapers in {list_scrapers}:\r\n\n"

        scrapers = []

        plugins_data = get_plugins_data(config.plugins)

        for plugin_namespace, _, plugin_hook_data in plugins_data:
            if list_scrapers == plugin_namespace:
                plugin_scrapers = plugin_hook_data["scrapers"]

                for scraper in plugin_scrapers:
                    if len(plugin_scrapers) != 1:
                        if scraper != "DEFAULT":
                            scrapers.append(f"- {Colours.PINK_GREY}{plugin_namespace}.{scraper}{Colours.RESET}\n")
                    else:
                        scrapers.append(f"- {Colours.PINK_GREY}{plugin_namespace}.{scraper}{Colours.RESET}\n")         
        
        if not scrapers:
            mov_cli_logger.error(f"Could not find plugin under namespace: {list_scrapers}")

            return None

        print(string + "\n".join(scrapers))
        return None

    plugins = config.plugins

    welcome_message = welcome_msg(
        plugins = plugins, 
        check_for_updates = True if query is None and config.skip_update_checker is False else False, 
        display_hint = True if query is None else False, 
        display_version = version
    )

    print(welcome_message)

    if query is not None:
        scrape_options = steal_scraper_args(query) 
        # This allows passing arguments to scrapers like this: 
        # https://github.com/mov-cli/mov-cli-youtube/commit/b538d82745a743cd74a02530d6a3d476cd60b808#diff-4e5b064838aa74a5375265f4dfbd94024b655ee24a191290aacd3673abed921a

        query: str = " ".join(query)

        http_client = HTTPClient(config)

        selected_scraper = select_scraper(plugins, config.fzf_enabled, config.default_scraper)

        if selected_scraper is None:
            mov_cli_logger.error(
                "You must choose a scraper to scrape with! " \
                    "You can set a default scraper with the default key in config.toml."
            )
            return False

        chosen_scraper = use_scraper(selected_scraper, config, http_client, scrape_options)

        choice = search(query, auto_select, chosen_scraper, config.fzf_enabled)

        if choice is None:
            mov_cli_logger.error("There was no results or you didn't select anything.")
            return False

        chosen_episode = handle_episode(
            episode_string = episode, 
            scraper = chosen_scraper, 
            choice = choice, 
            fzf_enabled = config.fzf_enabled
        )

        if chosen_episode is None:
            mov_cli_logger.error("You didn't select a season/episode.")
            return False

        media = scrape(choice, chosen_episode, chosen_scraper)

        if media.url is None:
            mov_cli_logger.error(
                "Scraper didn't return a streamable url." \
                    "\nThis is NOT a mov-cli issue. This IS an plugin issue"
            )
            return False

        if download:
            dl = Download(config)
            mov_cli_logger.debug(f"Downloading from this url -> '{media.url}'")

            popen = dl.download(media)
            popen.wait()

        else:
            option = play(media, choice, chosen_scraper, chosen_episode, config)

            if option == "search":
                query = input(Colours.BLUE.apply("  Enter Query: "))

                mov_cli(
                    query = [query], 
                    debug = debug, 
                    player = player, 
                    scraper = scraper, 
                    fzf = fzf,
                    episode = None,
                    auto_select = None,

                    version = False,
                    edit = False,
                    download = False
                )

def app():
    uwu_app.command()(mov_cli)
    uwu_app()
