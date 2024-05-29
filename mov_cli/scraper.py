from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, Literal, Iterable, Optional

    from .config import Config
    from .utils import EpisodeSelector
    from .http_client import HTTPClient
    from .media import Metadata, Multi, Single

    ScraperOptionsT = Dict[str, str | bool]

from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from devgoldyutils import LoggerAdapter

from .logger import mov_cli_logger

__all__ = (
    "Scraper",
)

class Scraper(ABC):
    """A base class for building scrapers from."""
    def __init__(
            self, 
            config: Config, 
            http_client: HTTPClient, 
            options: Optional[ScraperOptionsT] = None
        ) -> None:

        self.config = config
        self.http_client = http_client
        self.options = options or {}

        self.logger = LoggerAdapter(mov_cli_logger, prefix = self.__class__.__name__)

        super().__init__()

    def soup(self, html: str, **kwargs) -> BeautifulSoup:
        """A ready to use beautiful soup instance."""
        return BeautifulSoup(html, self.config.parser, **kwargs)

    @abstractmethod
    def search(self, query: str, limit: int = 20) -> Iterable[Metadata]:
        """Where your searching for media should be done. Should return or yield Metadata."""
        ...

    @abstractmethod
    def scrape(self, metadata: Metadata, episode: EpisodeSelector) -> Optional[Multi | Single]:
        """
        Where your scraping for the media should be performed. 
        Should return or yield an instance of Media.
        """
        ...

    def scrape_episodes(self, metadata: Metadata) -> Dict[int, int] | Dict[None, Literal[1]]:
        """Returns episode count for each season in that Movie/Series."""
        return {None: 1}