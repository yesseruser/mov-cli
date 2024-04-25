from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional

    from .. import Config
    from pathlib import Path
    from ..media import Media
    from ..utils.platform import SUPPORTED_PLATFORMS

import httpx
import subprocess
import unicodedata
from devgoldyutils import Colours, LoggerAdapter

from .. import errors
from .player import Player
from ..logger import mov_cli_logger
from ..utils import get_temp_directory

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
            with open('/dev/clipboard', 'w') as f:
                f.write(f"vlc://{media.url}")

            logger.info("The URL was copied into your clipboard. To play it, open a browser and paste the URL.")

            return None

        elif self.platform == "Linux" or self.platform == "Windows":
            try:
                args = [
                    "vlc", 
                    f'--meta-title="{media.display_name}"', 
                    media.url, 
                    "--quiet"
                ]

                if media.referrer is not None:
                    args.append(f'--http-referrer="{media.referrer}"')

                if media.audio_url is not None:
                    args.append(f"--input-slave={media.audio_url}") # WHY IS THIS UNDOCUMENTED!!!

                if media.subtitles is not None:
                    subtitles = media.subtitles

                    if subtitles.startswith("https://"):
                        logger.debug("Subtitles detected as a url.")
                        subtitles = str(self.__url_subtitles_to_file(media, subtitles))

                    args.append(f"--sub-file={subtitles}")

                if self.config.resolution is not None:
                    args.append(f"--adaptive-maxwidth={self.config.resolution}") # NOTE: I don't really know if that works ~ Ananas

                return subprocess.Popen(args)

            except (ModuleNotFoundError, FileNotFoundError):
                raise errors.PlayerNotFound(self)

        return None

    def __url_subtitles_to_file(self, media: Media, subtitles_url: str) -> Path:
        sub_file_exists_already = False
        temp_dir = get_temp_directory(self.platform)

        file_name = unicodedata.normalize("NFKD", media.display_name).encode("ascii", "ignore").decode("ascii")

        for path in temp_dir.iterdir():

            if path.name == file_name:
                sub_file_exists_already = True
                logger.debug("Subtitles already exists in temp directory, skipping download...")
                break

        file_path = temp_dir.joinpath(file_name)

        if sub_file_exists_already is False:
            logger.debug("Downloading subtitles to temp directory as vlc does not support streaming of subs via url...")
            response = httpx.get(url = subtitles_url)

            with file_path.open("wb") as file:
                file.write(response.content)

        return file_path