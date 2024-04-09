from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, Any
    from ..config import Config

import os
from subprocess import check_call, CalledProcessError

from .. import utils
from ..logger import mov_cli_logger

def set_cli_config(config: Config, **kwargs: Optional[Any]) -> Config:
    debug = kwargs.get("debug")
    player = kwargs.get("player")
    scraper = kwargs.get("scraper")
    fzf = kwargs.get("fzf")

    if debug is not None:
        config.data["debug"] = debug

    if player is not None:
        config.data["player"] = player

    if scraper is not None:
        if config.data.get("scrapers") is None:
            config.data["scrapers"] = {}

        config.data["scrapers"]["default"] = scraper

    if fzf is not None:
        if config.data.get("ui") is None:
            config.data["ui"] = {}

        config.data["ui"]["fzf"] = fzf

    return config

def open_config_file(config: Config):
    """Opens the config file in the respectable editor for that platform."""
    editor = config.editor

    if editor is None: 
        platform = utils.what_platform()
        env_editor = os.environ.get("EDITOR")        

        if env_editor is not None:
            editor = env_editor
        else:
            if platform == "Windows":
                editor = "notepad"
            elif platform == "Darwin":
                editor = "nano" # NOTE: https://support.apple.com/guide/terminal/use-command-line-text-editors-apdb02f1133-25af-4c65-8976-159609f99817/mac
            elif platform == "iOS":
                editor = "vi"
            elif platform == "Linux" or platform == "Android":
                editor = "nano"

    mov_cli_logger.debug("Opening config file...")

    try:
        check_call([editor, config.config_path])
    except (FileNotFoundError, CalledProcessError) as e:
        mov_cli_logger.error(
            f"Failed to open config file with the editor '{editor}'! Error: {e}" \
                f"\nYou can manually edit it over here: '{config.config_path}'."
        )