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

__all__ = ("IINA",)

class IINA(Player):
    def __init__(self, platform: SUPPORTED_PLATFORMS, config: Config, **kwargs) -> None:
        self.config = config
        self.platform = platform

        super().__init__(display_name = Colours.GREY.apply("IINA"), **kwargs)

    def play(self, media: Media) -> Optional[subprocess.Popen]:
        """Plays this media in the IINA media player for MacOS."""

        if self.platform == "Darwin":
            args = [
                "iina",
                "--keep-running",
                media.url,
                f"--mpv-force-media-title={media.display_name}",
            ]

            if media.referrer is not None:
                args.append(f"--mpv-referrer={media.referrer}")

            if media.audio_url is not None: # TODO: This will need testing.
                args.append(f"--mpv-audio-file={media.audio_url}")

            if media.subtitles is not None: # TODO: This will need testing.

                for subtitle in media.subtitles:
                    args.append(f"--mpv-sub-file={subtitle}")

            if self.config.resolution is not None:
                args.append(f"--mpv-hls-bitrate={self.config.resolution}") # NOTE: This only works when the file is a m3u8

            if self.config.debug_player is False:
                args.append("--no-stdin")

            return subprocess.Popen(args)

        return None