from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Callable, Optional, Tuple

import warnings
from enum import Enum
from datetime import datetime
from devgoldyutils import Colours
from dataclasses import dataclass, field

__all__ = (
    "MetadataType",
    "Metadata",
    "ExtraMetadata",
    "AiringType"
)

class MetadataType(Enum):
    MULTI = 0
    """Media with multiple seasons and episodes."""
    SINGLE = 1
    """Media with no seasons and episodes. Like a film or short animation."""

class AiringType(Enum):
    DONE = 0
    ONGOING = 1
    NOT_RELEASED = 2

@dataclass
class Metadata:
    """
    Essentially search result objects that are returned from scrapers when searching.
    """

    id: str
    """
    A unique ID to represent this content so 
    mov-cli can uniquely identify from one another.
    """
    title: str
    """Title of the content. Will be used to display in the selector."""
    type: MetadataType
    """
    The type of metadata. Does it have multiple 
    seasons and episodes or is it just a singular release.
    """
    description: Optional[str] = field(default = None)
    """Description of the content to display in fzf preview."""
    image_url: Optional[str] = field(default = None)
    """Image URL to a banner, cover or thumbnail of this media."""
    alternate_titles: Optional[List[str]] = field(default = None)
    """A list of alternative titles for this content."""
    cast: Optional[List[str] ]= field(default = None) # TODO: Give these docstring descriptions.
    genres: Optional[List[str]] = field(default = None)
    airing: Optional[AiringType] = field(default = None)
    release_date: Optional[datetime] = field(default = None)
    """The date and time the content was released."""
    year: Optional[str] = field(default = None)
    """DEPRECATED!!! The year the content was released."""

    extra_func: Optional[Callable[[], ExtraMetadata]] = field(default = None)
    """DEPRECATED!!! Callback that returns extra metadata."""

    # NOTE: we can remove this function in v4.6 when 'year' and 'extra_func' is removed.
    def __post_init__(self):
        if self.release_date is not None and self.year is not None:
            raise TypeError(
                "You shouldn't use both 'release_date' and 'year' params. " \
                    "Use one, and you should use 'release_date' as the 'year' param is now deprecated."
            )

        if self.year is not None:
            warnings.warn(
                "The parameter 'year' is now deprecated! The param 'release_date' " \
                    "should be used instead because 'year' is gonna be removed in v4.6.",
                category = DeprecationWarning,
                stacklevel = 3
            )

            self.release_date = datetime(year = int(self.year), month = 1, day = 1)

        if self.extra_func is not None:
            warnings.warn(
                "The parameter 'extra_func' is now deprecated! It's being getting " \
                    "removed in v4.6 as ExtraMetadata has now been merged with Metadata.",
                category = DeprecationWarning,
                stacklevel = 3
            )

    @property
    def display_name(self) -> str:
        """How the metadata title should be displayed in selectors (e.g. fzf)."""
        return f"{Colours.BLUE if self.type == MetadataType.SINGLE else Colours.PINK_GREY}{self.title}" \
            f"{Colours.RESET} ({self.display_release_date})"

    @property
    def display_release_date(self) ->  str:
        "How the release date is displayed in selectors (e.g. fzf)."
        return str(self.release_date.year) if self.release_date is not None else ""


# This is deprecated now but let's give plugin 
# developers time to stop using it then we'll remove it in v4.6
@dataclass 
class ExtraMetadata():
    """More in-depth metadata about media."""
    description: Optional[str]
    """Description of Series, Film or TV Station."""
    alternate_titles: List[str] | Tuple[str, str] | None = field(default = None)

    cast: List[str] | None = field(default = None)
    genres: List[str] | None = field(default = None)
    airing: AiringType | None = field(default = None)