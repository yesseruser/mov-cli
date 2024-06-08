from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, Callable

    from ..media import Metadata
    from ..scraper import Scraper

from devgoldyutils import Colours

from .ui import prompt
from .auto_select import auto_select_choice
from .plugins import handle_internal_plugin_error

from ..cache import Cache
from ..logger import mov_cli_logger
from ..utils import what_platform, get_temp_directory

class ImageURLCache(Cache):
    def __init__(self) -> None:
        platform = what_platform()
        temp_dir = get_temp_directory(platform)

        self._basic_cache_file_path = temp_dir.joinpath("image_url_cache")

def cache_image_for_preview(cache: ImageURLCache) -> Callable[[Metadata], Metadata]:

    def before_display_callable(metadata: Metadata) -> Metadata:
        cache.set_cache(metadata.title, metadata.image_url)

        return metadata

    return before_display_callable

def search(query: str, auto_select: Optional[int], scraper: Scraper, fzf_enabled: bool, limit: Optional[int]) -> Optional[Metadata]:
    choice = None
    cache = ImageURLCache()

    mov_cli_logger.info(f"Searching for '{Colours.ORANGE.apply(query)}'...")

    try:
        search_results = scraper.search(query, limit)
    except Exception as e:
        handle_internal_plugin_error(e)

    if auto_select is not None:
        choice = auto_select_choice((choice for choice in search_results), auto_select)
    else:
        choice = prompt(
            "Choose Result", 
            choices = (choice for choice in search_results), 
            display = lambda x: x.display_name, 
            fzf_enabled = fzf_enabled,
            before_display = cache_image_for_preview(cache)
        )

    cache.clear_all_cache()

    return choice