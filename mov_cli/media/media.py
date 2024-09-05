from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, List

    from ..utils import EpisodeSelector

import json
import shutil
import warnings
import subprocess
from abc import abstractmethod
from deprecation import deprecated
from devgoldyutils import LoggerAdapter

from ..logger import mov_cli_logger

from .quality import Quality
from .subtitle import Subtitle
from .audio_track import AudioTrack

__all__ = (
    "Media", 
    "Multi", 
    "Single"
)

logger = LoggerAdapter(mov_cli_logger, prefix = "Media")

class Media():
    """Represents any piece of media in mov-cli that can be streamed or downloaded."""
    def __init__(
        self,
        url: str,
        title: str,
        audio_url: Optional[str],
        audio_tracks: Optional[List[AudioTrack]],
        referrer: Optional[str],
        subtitles: Optional[List[Subtitle]]
    ) -> None:
        if audio_url is not None:
            warnings.warn(
                "The parameter 'audio_url=' is deprecated!!! It will be removed in v4.6! Use 'audio_tracks=' instead.",
                category = DeprecationWarning,
                stacklevel = 3
            )

            audio_tracks = [AudioTrack(audio_url)]

        if isinstance(subtitles, list):
            warnings.warn(
                "The parameter 'subtitles=' should now be a list of Subtitle objects! " \
                    "Passing strings into 'subtitles=' will break in v4.6!",
                category = DeprecationWarning,
                stacklevel = 3
            )
            subtitles = [Subtitle(url = subtitle_url) for subtitle_url in subtitles]

        self.url = url
        """The stream-able url of the media (Can also be a path to a file). """
        self.title = title
        """A raw title of the media."""
        self.audio_tracks = audio_tracks
        """
        A list of streamable audio tracks to stream alongside the video.
        The list should be in order of priority because if the main stream has no audio, 
        some players will only play the first audio track.
        """
        self.referrer = referrer
        """A required referrer url for the player to be able to stream the content."""
        self.subtitles = subtitles
        """A list of subtitles for the player to devour. (⚈₋₍⚈)"""

        self.__stream_quality: Optional[Quality] = None

    @property
    @abstractmethod
    def display_title(self) -> str:
        """
        The title that should be displayed by the player. (includes attributes like episode and season)
        """
        ...

    @property
    @deprecated(
        deprecated_in = "4.5",
        removed_in = "4.6",
        details = "The property 'Media.display_name' is deprecated!!! " \
            "Use 'Media.display_title' instead. This will be removed next major release (v4.6)!"
    )
    def display_name(self) -> None:
        return self.display_title

    def get_quality(self) -> Optional[Quality]:
        """Uses ffprode to grab the quality of the stream."""

        if self.__stream_quality is None:

            if shutil.which("ffprobe") is None:
                return None

            args = [
                "ffprobe", 
                "-v", 
                "error", 
                "-select_streams", 
                "v", 
                "-show_entries", 
                "stream=width,height", 
                "-of",
                "json",
                self.url
            ]

            out = str(subprocess.check_output(args), "utf-8")

            stream = json.loads(out).get("streams", [])

            if not stream == []:
                width = stream[0]["width"]
                height = stream[0]["height"]

                target_dimension_px = height

                if height > width:
                    target_dimension_px = width

                heights_lower_than_target_height = [
                    quality_height for quality_height in Quality._value2member_map_ if target_dimension_px >= quality_height
                ]

                closest_quality_height = min(heights_lower_than_target_height, key = lambda x: abs(x - target_dimension_px))

                self.__stream_quality = Quality(closest_quality_height)

        return self.__stream_quality

class Multi(Media):
    """Represents a media that has multiple episodes like a TV Series, Anime or Cartoon."""
    def __init__(
        self,
        url: str,
        title: str,
        episode: EpisodeSelector,
        audio_url: Optional[str] = None,
        audio_tracks: Optional[List[AudioTrack]] = None,
        referrer: Optional[str] = None,
        subtitles: Optional[List[Subtitle]] = None
    ) -> None:
        self.episode = episode
        """The episode and season of this series."""

        super().__init__(
            url,
            title = title,
            audio_url = audio_url,
            audio_tracks = audio_tracks,
            referrer = referrer,
            subtitles = subtitles
        )

    @property
    def display_name(self) -> str:
        return f"{self.title} - S{self.episode.season} EP{self.episode.episode}"

class Single(Media):
    """Represents a media with a single episode, like a Film/Movie or a YouTube video."""
    def __init__(
        self,
        url: str,
        title: str,
        audio_url: Optional[str] = None,
        audio_tracks: Optional[List[AudioTrack]] = None,
        referrer: Optional[str] = None,
        year: Optional[str] = None,
        subtitles: Optional[List[Subtitle]] = None
    ) -> None:
        self.year = year
        """The year this film was released."""

        super().__init__(
            url,
            title = title,
            audio_url = audio_url,
            audio_tracks = audio_tracks,
            referrer = referrer,
            subtitles = subtitles
        )

    @property
    def display_name(self) -> str:
        return f"{self.title} ({self.year})" if self.year is not None else self.title