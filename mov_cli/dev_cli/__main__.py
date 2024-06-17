from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, List

import os
import json
import typer
import httpx
import shutil
from pathlib import Path
from subprocess import call
from devgoldyutils import Colours

from ..cache import Cache
from ..utils import what_platform, get_temp_directory

__all__ = ()

app = typer.Typer(
    pretty_exceptions_enable = False, 
    help = "Developer only commands to be executed from scripts and assist with testing and development of mov-cli plugins and more."
)

test_app = typer.Typer(name = "test", help = "Run tests on mov-cli plugins and other varies mov-cli functionalities.")

test_misc_app = typer.Typer(name = "misc", help = "")
test_app.add_typer(test_misc_app)

preview_app = typer.Typer(name = "preview", help = "Dev command used by stuff like fzf to display images from mov-cli in the terminal.")

app.add_typer(test_app)
app.add_typer(preview_app)

@test_misc_app.command(help = "Test how a tip that get's displayed under the mov-cli welcome message is displayed.")
def tip(tip_index: int):
    mov_cli_path = Path(__file__).parent.parent
    random_tips_path = mov_cli_path.joinpath("cli", "random_tips.json")

    random_tips_json: List[str] = json.load(random_tips_path.open("r"))

    print(f"\n- {Colours.ORANGE}TIP: {Colours.RESET}{random_tips_json[tip_index]}\n")

@preview_app.command(help = "Preview image from mov-cli cache to terminal.")
def image(id: str):
    platform = what_platform()

    if not platform == "Linux":
        print("Image preview only works on Linux atm.")
        return False

    cache = Cache(
        platform = platform, 
        section = "image_urls"
    )

    image_url = cache.get_cache(id)

    if image_url is None:
        print("No Image :(")
        return False

    fzf_preview_lines = os.environ["FZF_PREVIEW_LINES"] # height
    fzf_preview_columns = os.environ["FZF_PREVIEW_COLUMNS"] # width

    os.system("clear")

    if "KITTY_WINDOW_ID" in os.environ:
        call([
            "kitty", 
            "icat", 
            "--clear", 
            "--transfer-mode=memory", 
            "--unicode-placeholder", 
            "--stdin=no", 
            f"--place={fzf_preview_columns}x{fzf_preview_lines}@0x0", 
            image_url
        ])

    elif shutil.which("chafa") is not None:
        file = image_url_to_file(image_url, id, platform).resolve()

        call([
            "chafa", 
            file, 
            f"--size={fzf_preview_columns}x{fzf_preview_lines}"
        ])

    else:
        print("'chafa' was not found! :( Please install it: https://github.com/hpjansson/chafa")
        return False


def image_url_to_file(image_url: str, id: str, platform: str) -> Optional[Path]:
    temp = get_temp_directory(platform)
    file = temp.joinpath(f"{id}")

    request = httpx.get(image_url)

    if request.is_error:
        return None
    
    if file.exists():
        return file
    
    with file.open("wb") as f:
        f.write(request.content)
    
    return file