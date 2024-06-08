from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    ...

import typer

__all__ = ()

app = typer.Typer(
    pretty_exceptions_enable = False, 
    help = "A developer only command to assist with testing and development of mov-cli plugins."
)

test_app = typer.Typer(name = "test", help = "Run tests on varies mov-cli functionalities.")

app.add_typer(test_app)

@test_app.command(help = "Automatically tests the **entire** plugin for faults.")
def plugin(
    plugin_name: str = typer.Argument(help = "The name of the plugin to test."), 
    query: str = typer.Argument("*", help = "The query to use if searching is being tested.")
):
    # NOTE: I'll be using a series of pytest tests here.
    ...