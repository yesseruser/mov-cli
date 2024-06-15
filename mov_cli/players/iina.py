from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, List

    from ..media import Media
    from ..utils.platform import SUPPORTED_PLATFORMS

import subprocess
from devgoldyutils import Colours

from .player import Player

__all__ = ("IINA",)

class IINA(Player):
    def __init__(
        self, 
        platform: SUPPORTED_PLATFORMS, 
        player_args: Optional[List[str]] = None, 
        debug: bool = False, 
        **kwargs
    ) -> None:
        self.display_name = Colours.GREY.apply("IINA")

        super().__init__(
            platform = platform, 
            player_args = player_args,
            debug = debug
        )

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

            if self.debug is False:
                args.append("--no-stdin")

            return subprocess.Popen(args)

        return None