from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional

    from .. import Config
    from ..media import Media
    from ..utils.platform import SUPPORTED_PLATFORMS

import subprocess
from ..media.quality import Quality

from .player import Player

__all__ = ("MPV_TTY",)

class MPV_TTY(Player):
    def __init__(self, platform: SUPPORTED_PLATFORMS, config: Config, **kwargs) -> None:
        self.platform = platform
        self.config = config

        super().__init__(display_name = "MPV-TTY", **kwargs)

    def play(self, media: Media) -> Optional[subprocess.Popen]:
        """Plays this media in the TTY using MPV."""

        if self.platform == "Linux" or self.platform == "Windows" or self.platform == "Darwin":
            args = [
                "mpv", 
                "--vo=tct", 
                media.url
            ]

            if media.referrer is not None:
                args.append(f"--referrer={media.referrer}")

            if media.audio_url is not None:
                args.append(f"--audio-file={media.audio_url}")

            if not self.config.resolution == Quality.AUTO:
                args.append(f"--hls-bitrate={self.config.resolution.value}") # NOTE: This only works when the file is a m3u8

            return subprocess.Popen(args)

        return None