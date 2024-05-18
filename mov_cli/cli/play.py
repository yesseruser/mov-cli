from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, Literal

    from ..config import Config
    from ..scraper import Scraper
    from ..media import Media, Metadata

    from utils.episode_selector import EpisodeSelector

from devgoldyutils import Colours

from .scraper import scrape
from .episode import handle_episode
from .watch_options import watch_options

from ..media import MetadataType
from ..utils import what_platform, hide_ip
from ..logger import mov_cli_logger

def play(media: Media, metadata: Metadata, scraper: Scraper, episode: EpisodeSelector, config: Config) -> Optional[Literal["search"]]:
    platform = what_platform()

    chosen_player = config.player

    episode_details_string = ""

    if metadata.type == MetadataType.MULTI:
        season_string = Colours.CLAY.apply(str(episode.season))
        episode_string = Colours.ORANGE.apply(str(episode.episode))

        episode_details_string = f"episode {episode_string} in season {season_string} of " if episode.season > 1 else f"episode {episode_string} of "

    mov_cli_logger.info(
        f"Playing {episode_details_string}'{Colours.BLUE.apply(media.title)}' " \
            f"with {chosen_player.display_name}..."
    )
    mov_cli_logger.debug(f"Streaming with this url -> '{hide_ip(media.url, config)}'")

    try:
        popen = chosen_player.play(media)
    except FileNotFoundError as e:
        mov_cli_logger.error(
            f"The player '{chosen_player.display_name}' was not found! " \
                f"Are you sure you have it installed? Are you sure it's in path? \nError: {e}"
        )
        return None

    if popen is None and platform != "iOS":
        mov_cli_logger.error(
            f"The player '{chosen_player.display_name}' is not supported on this platform ({platform}). " \
            "We recommend VLC for iOS, IINA for MacOS and MPV for every other platform."
        )

        return None

    option = watch_options(popen, chosen_player, platform, media, config.fzf_enabled)

    if option == "next" or option == "previous":
        popen.kill()

        media_episodes = scraper.scrape_episodes(metadata)

        if option == "next":
            episode.episode += 1
        else:
            episode.episode -= 1

        season_episode_count = media_episodes.get(episode.season)

        if season_episode_count is None:
            mov_cli_logger.info("No more episodes :(")
            return None

        result = __handle_next_season(episode, season_episode_count, media_episodes)

        if result is False:
            mov_cli_logger.info("No more episodes :(")
            return None

        media = scrape(metadata, episode, scraper)

        return play(media, metadata, scraper, episode, config)

    elif option == "select":
        popen.kill()

        episode = handle_episode(None, scraper, metadata, config.fzf_enabled)

        if episode is None:
            return None

        media = scrape(metadata, episode, scraper)

        return play(media, metadata, scraper, episode, config)

    popen.wait()

    return None

def __handle_next_season(episode: EpisodeSelector, season_episode_count: int, media_episodes: dict) -> bool:

    if episode.episode > season_episode_count:
        next_season = episode.season + 1

        if media_episodes.get(next_season) is None:
            return False

        episode._next_season()

    elif episode.episode <= 1:

        if episode.season <= 1:
            return False

        episode._previous_season()

    return True
