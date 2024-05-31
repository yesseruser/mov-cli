from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

from enum import Enum
import subprocess
import shutil
import json


__all__ = ("Quality", "get_quality",)

class Quality(Enum):
    SD = 480
    HD = 720
    FHD = 1080
    QHD = 1440
    UHD = 2160

    _2K = QHD
    _4K = UHD

    AUTO = 0

    def __init__(self, pixel: int) -> None:
        ...

    def apply_p(self) -> str:
        """Returns that enum but with an ending p."""
        return f"{self.value}p"

def get_quality(url: str | Path) -> Quality | None:
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
        url
    ]

    out = str(subprocess.check_output(args), "utf-8")

    stream = json.loads(out)["streams"][0]

    if stream is not None:
        height = stream["height"]

        if height in Quality._value2member_map_:
            return Quality(height)

    return None