from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional
    from ..media import Media
    from .. import Config
    from ..utils.platform import SUPPORTED_PLATFORMS

import subprocess
from devgoldyutils import Colours

from .player import Player

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
                "--no-terminal",
            ]

            if media.referrer is not None:
                args.append(f"--referrer={media.referrer}")

            if media.audio_url is not None:
                args.append(f"--audio-file={media.audio_url}")

            if media.subtitles is not None:
                args.append(f"--sub-file={media.subtitles}")

            if self.config.resolution is not None:
                args.append(f"--hls-bitrate={self.config.resolution.value}") # NOTE: This only works when the file is a m3u8

            return subprocess.Popen(args)

        return None