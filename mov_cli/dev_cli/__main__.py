from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    ...

import typer
from subprocess import call

from ..cache import Cache
from ..utils import what_platform

__all__ = ()

app = typer.Typer(
    pretty_exceptions_enable = False, 
    help = "Developer only commands to be executed from scripts and assist with testing and development of mov-cli plugins."
)

test_app = typer.Typer(name = "test", help = "Run tests on plugins varies mov-cli functionalities.")
preview_app = typer.Typer(name = "preview", help = "Dev command used by stuff like fzf to display images from mov-cli in the terminal.")

app.add_typer(test_app)
app.add_typer(preview_app)

@preview_app.command(help = "Preview image from mov-cli cache to terminal.")
def image(id: str):
    cache = Cache(
        platform = what_platform(), 
        section = "image_urls"
    )

    image_url = cache.get_cache(id)

    if image_url is None:
        print("No Image :(")
    else:
        call(["fzf-preview.sh", image_url])