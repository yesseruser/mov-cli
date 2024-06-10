from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional

import httpx

from pathlib import Path

from .paths import get_temp_directory
from .platform import what_platform

__all__ = ("save", )

def save(url: str, save_name: str) -> Optional[Path]:
    platform = what_platform()
    temp = get_temp_directory(platform)
    file = temp.joinpath(f"{save_name}")

    request = httpx.get(url)

    if request.is_error:
        return None
    
    if file.exists():
        return file
    
    with file.open("wb") as f:
        f.write(request.content)
    
    return file