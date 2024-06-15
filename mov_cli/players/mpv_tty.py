from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, List

    from ..media import Media
    from ..utils.platform import SUPPORTED_PLATFORMS

import subprocess

from .player import Player

__all__ = ("MPV_TTY",)

class MPV_TTY(Player):
    def __init__(
        self, 
        platform: SUPPORTED_PLATFORMS, 
        player_args: Optional[List[str]] = None, 
        debug: bool = False, 
        **kwargs
    ) -> None:
        self.display_name = "MPV-TTY"

        super().__init__(
            platform = platform, 
            player_args = player_args,
            debug = debug
        )

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

            return subprocess.Popen(args)

        return None