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

__all__ = ("VLC",)

logger = LoggerAdapter(mov_cli_logger, prefix = Colours.ORANGE.apply("VLC"))

class VLC(Player):
    def __init__(self, platform: SUPPORTED_PLATFORMS, config: Config, **kwargs) -> None:
        self.platform = platform
        self.config = config

        super().__init__(**kwargs)

    def play(self, media: Media) -> Optional[subprocess.Popen]:
        """Plays this media in the VLC media player."""

        logger.info("Launching VLC Media Player...")

        if self.platform == "Android":
            return subprocess.Popen(
                [
                    "am",
                    "start",
                    "-n",
                    "org.videolan.vlc/org.videolan.vlc.gui.video.VideoPlayerActivity",
                    "-e",
                    "title",
                    media.display_name,
                    media.url,
                ]
            )

        elif self.platform == "iOS":
            logger.debug("Detected your using iOS. \r\n")

            with open('/dev/clipboard', 'w') as f:
                f.write(f"vlc://{media.url}")

            logger.info("The URL was copied into your clipboard. To play it, open a browser and paste the URL.")

            return None

        elif self.platform == "Linux" or self.platform == "Windows":
            try:
                args = [
                    "vlc", 
                    f'--meta-title="{media.display_name}"', 
                    media.url
                ]

                if media.referrer is not None:
                    args.append(f'--http-referrer="{media.referrer}"')

                if self.config.resolution:
                    args.append(f"--adaptive-maxwidth={self.config.resolution}") # NOTE: I don't really know if that works ~ Ananas

                return subprocess.Popen(args)

            except ModuleNotFoundError:
                raise errors.PlayerNotFound(self)

        return None