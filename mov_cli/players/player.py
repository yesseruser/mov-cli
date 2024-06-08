from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, List

    from ..media import Media

import subprocess
from devgoldyutils import Colours
from abc import ABC, abstractmethod

__all__ = ("Player",)

class Player(ABC):
    """A base class for all players in mov-cli."""
    def __init__(self, display_name: Optional[str] = None, player_args: Optional[List[str]] = None, **kwargs) -> None:
        self.player_args = player_args
        self.display_name = display_name or Colours.PINK_GREY.apply(self.__class__.__name__)

        super().__init__()

    @abstractmethod
    def play(self, media: Media) -> Optional[subprocess.Popen]:
        """Method to be overridden with code to play media in that specific player."""
        ...