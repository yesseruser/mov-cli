from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional

from dataclasses import dataclass, field

__all__ = ("AudioTrack", )

@dataclass
class AudioTrack:
    url: str
    name: Optional[str] = field(default = None)

    def __post_init__(self):
        ...