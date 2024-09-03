from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..scraper import ScrapeEpisodesT

from dataclasses import dataclass, field

__all__ = ("EpisodeSelector",)

@dataclass
class EpisodeSelector:
    """Swift util to use when asking the scraper which episode of a show to scrape."""
    episode: int = field(default = 1)
    season: int = field(default = 1)

    # NOTE: I made it private as I don't want library devs using 
    # this method yet because it may drastically change in the future.
    def _next_season(self) -> None:
        self.episode = 1
        self.season += 1

    def _previous_season(self, media_episodes: ScrapeEpisodesT) -> None:
        self.season -= 1
        self.episode = media_episodes.get(self.season, 1)