from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional
    from ..utils import EpisodeSelector

from abc import abstractmethod

__all__ = (
    "Media",
    "Multi", 
    "Single", 
    "Movie", 
    "Series"
)

class Media():
    """Represents any piece of media in mov-cli that can be streamed or downloaded."""
    def __init__(self, url: str, title: str, referrer: Optional[str]) -> None:
        self.url = url
        """The stream-able url."""
        self.title = title
        """A title to represent this stream-able media."""
        self.referrer = referrer
        """The required referrer for streaming the media content."""

    @property
    @abstractmethod
    def display_name(self) -> str:
        """The title that should be displayed by the player."""
        ...

class Multi(Media):
    """Represents a media that has multiple episodes like a TV Series, Anime or Cartoon."""
    def __init__(
        self, 
        url: str, 
        title: str, 
        episode: EpisodeSelector, 
        referrer: Optional[str] = None, 
        subtitles: Optional[dict] = None
    ) -> None:
        self.episode = episode
        """The episode and season of this series."""
        self.subtitles = subtitles

        super().__init__(
            url, title, referrer
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
        referrer: Optional[str] = None,
        year: Optional[str] = None,
        subtitles: Optional[dict] = None
    ) -> None:
        self.year = year
        """The year this film was released."""
        self.subtitles = subtitles

        super().__init__(
            url, title, referrer
        )

    @property
    def display_name(self) -> str:
        return f"{self.title} ({self.year})"

# Backwards compatibility for post v4.3.0 extensions.
Series = Multi
Movie = Single