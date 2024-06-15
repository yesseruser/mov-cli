from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, List

    from ..media import Media
    from ..utils.platform import SUPPORTED_PLATFORMS

import subprocess
from devgoldyutils import Colours

from .player import Player

__all__ = ("SyncPlay",)

class SyncPlay(Player):
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
        return Colours.BLUE.apply("Syncplay")

    def play(self, media: Media) -> Optional[subprocess.Popen]:
        """Plays this media in SyncPlay."""
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

                for subtitle in media.subtitles:
                    args.append(f"--sub-file={subtitle}")

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

            if media.audio_url is not None: # NOTE: Let us know if this works.
                args.append(f"--mpv-audio-file={media.audio_url}")

            if media.subtitles is not None: # NOTE: Let us know if this works.

                for subtitle in media.subtitles:
                    args.append(f"--mpv-sub-file={media.subtitles}")

            if self.debug is False: # NOTE: Needs testing.
                args.append("--mpv-no-terminal")

            return subprocess.Popen(args)

        return None