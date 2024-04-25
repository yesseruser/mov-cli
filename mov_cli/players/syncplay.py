from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional
    from ..media import Media
    from .. import Config
    from ..utils.platform import SUPPORTED_PLATFORMS

import subprocess
from devgoldyutils import Colours, LoggerAdapter

from .. import errors
from ..logger import mov_cli_logger
from .player import Player

__all__ = ("SyncPlay",)

logger = LoggerAdapter(mov_cli_logger, prefix = Colours.PURPLE.apply("SyncPlay"))

class SyncPlay(Player):
    def __init__(self, platform: SUPPORTED_PLATFORMS, config: Config, **kwargs) -> None:
        self.platform = platform
        self.config = config

        super().__init__(**kwargs)

    def play(self, media: Media) -> Optional[subprocess.Popen]:
        """Plays this media in SyncPlay."""

        logger.info("Launching SyncPlay...")

        try:

            if self.platform == "Windows" or self.platform == "Linux":
                args = [
                    "syncplay",
                    media.url,
                    "--",
                    f"--force-media-title={media.display_name}",
                ]

                if media.referrer is not None:
                    args.append(f"--referrer={media.referrer}")

                if media.audio_url is not None:
                    args.append(f"--audio-file={media.audio_url}")

                if media.subtitles is not None:
                    args.append(f"--sub-file={media.subtitles}")

                if self.config.resolution is not None:
                    args.append(f"--hls-bitrate={self.config.resolution}") # NOTE: Only M3U8

                return subprocess.Popen(args)

            elif self.platform == "Darwin": # NOTE: Limits you to IINA
                args = [
                    "syncplay",
                    media.url,
                    "--",
                    f"--mpv-force-media-title={media.display_name}",
                ]

                if media.referrer is not None:
                    args.append(f"--mpv-referrer={media.referrer}")

                if media.audio_url is not None: # TODO: This will need testing.
                    args.append(f"--mpv-audio-file={media.audio_url}")

                if media.subtitles is not None: # TODO: This will need testing.
                    args.append(f"--mpv-sub-file={media.subtitles}")

                if self.config.resolution is not None: # TODO: This will need testing.
                    args.append(f"--mpv-hls-bitrate={self.config.resolution}")

                return subprocess.Popen(args)

        except (ModuleNotFoundError, FileNotFoundError):
            raise errors.PlayerNotFound(self)

        return None