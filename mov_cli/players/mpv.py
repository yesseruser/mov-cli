from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from typing import Optional

    from ..media import Media
    from ..utils.platform import SUPPORTED_PLATFORMS

import subprocess
from devgoldyutils import Colours

from .player import Player

__all__ = ("MPV",)

class MPV(Player):
    def __init__(
        self, 
        platform: SUPPORTED_PLATFORMS, 
        player_args: Optional[List[str]] = None, 
        debug: bool = False, 
        **kwargs
    ) -> None:
        super().__init__(
            platform = platform, 
            player_args = player_args,
            debug = debug
        )

    @property
    def display_name(self) -> str:
        return Colours.PURPLE.apply("MPV")

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

            if self.debug is False:
                args.append("--no-terminal")

            return subprocess.Popen(args)

        return None