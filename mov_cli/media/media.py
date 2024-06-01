from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional
    from ..utils import EpisodeSelector

import json
import shutil
import subprocess
from .quality import Quality

from abc import abstractmethod

__all__ = (
    "Media", 
    "Multi", 
    "Single"
)

class Media():
    """Represents any piece of media in mov-cli that can be streamed or downloaded."""
    def __init__(
        self, 
        url: str, 
        title: str, 
        audio_url: Optional[str], 
        referrer: Optional[str], 
        subtitles: Optional[str]
    ) -> None:
        self.url = url
        """The stream-able url of the media (Can also be a path to a file). """
        self.title = title
        """A title to represent this stream-able media."""
        self.audio_url = audio_url
        """The stream-able url that provides audio for the media if the main url doesn't stream with audio."""
        self.referrer = referrer
        """The required referrer for streaming the media content."""
        self.subtitles = subtitles
        """The url or file path to the subtitles."""

        self.__stream_quality: Optional[Quality] = None

    @property
    @abstractmethod
    def display_name(self) -> str:
        """The title that should be displayed by the player."""
        ...

    def get_quality(self) -> Optional[Quality]:
        """Uses ffprode to grab the quality of the stream."""

        if self.__stream_quality is None:

            if not shutil.which("ffprobe"):
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

            if stream:
                height = stream[0]["height"]
                width = stream[0]["width"]

                if height in Quality._value2member_map_:
                    self.__stream_quality = Quality(height)

                if width in Quality._value2member_map_:
                    self.__stream_quality = Quality(width)

        return self.__stream_quality

class Multi(Media):
    """Represents a media that has multiple episodes like a TV Series, Anime or Cartoon."""
    def __init__(
        self,
        url: str,
        title: str,
        episode: EpisodeSelector,
        audio_url: Optional[str] = None,
        referrer: Optional[str] = None,
        subtitles: Optional[str] = None
    ) -> None:
        self.episode = episode
        """The episode and season of this series."""

        super().__init__(
            url, 
            title = title, 
            audio_url = audio_url, 
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
        referrer: Optional[str] = None, 
        year: Optional[str] = None, 
        subtitles: Optional[str] = None
    ) -> None:
        self.year = year
        """The year this film was released."""

        super().__init__(
            url, 
            title = title, 
            audio_url = audio_url, 
            referrer = referrer,
            subtitles = subtitles
        )

    @property
    def display_name(self) -> str:
        return f"{self.title} ({self.year})" if self.year is not None else self.title