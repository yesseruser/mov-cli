from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional

    from .. import Config
    from ..media import Media
    from ..utils.platform import SUPPORTED_PLATFORMS

import subprocess
from devgoldyutils import Colours

from .player import Player
from ..media.quality import Quality

__all__ = ("MPV",)

class MPV(Player):
    def __init__(self, platform: SUPPORTED_PLATFORMS, config: Config, **kwargs) -> None:
        self.platform = platform
        self.config = config

        super().__init__(display_name = Colours.PURPLE.apply("MPV"), **kwargs)

    def play(self, media: Media) -> Optional[subprocess.Popen]:
        """Plays this media in the MPV media player."""

        if self.platform == "Android":
            return subprocess.Popen(
                [
                    "am",
                    "start",
                    "-n",
                    "is.xyz.mpv/is.xyz.mpv.MPVActivity",
                    "-e",
                    "filepath",
                    media.url,
                ]
            )

        elif self.platform == "Linux" or self.platform == "Windows" or self.platform == "Darwin":
            args = [
                "mpv",
                media.url,
                f"--force-media-title={media.display_name}",
            ]

            if media.referrer is not None:
                args.append(f"--referrer={media.referrer}")

            if media.audio_url is not None:
                args.append(f"--audio-file={media.audio_url}")

            if media.subtitles is not None:

                for subtitle in media.subtitles:
                    args.append(f"--sub-file={subtitle}")

            if not self.config.resolution == Quality.AUTO:
                args.append(f"--hls-bitrate={self.config.resolution.value}") # NOTE: This only works when the file is a m3u8

            if self.config.debug_player is False:
                args.append("--no-terminal")

            return subprocess.Popen(args)

        return None