from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import (
        Any, Dict, List, Tuple, 
        TypeVar, Literal, Iterable, Callable, Generator
    )

    T = TypeVar('T')

import re
import os
import json
import types
import random
import logging
import getpass
import inquirer
import itertools
from pathlib import Path
from datetime import datetime
from inquirer.themes import Default
from devgoldyutils import Colours, LoggerAdapter

import mov_cli

from ..iterfzf import iterfzf
from ..logger import mov_cli_logger
from ..utils import  what_platform, update_available, plugin_update_available

__all__ = (
    "prompt", 
)

logger = LoggerAdapter(mov_cli_logger, prefix = Colours.PURPLE.apply("prompt"))

class MovCliTheme(Default):
    def __init__(self):
        super().__init__()
        self.Question.mark_color = Colours.BLUE.value
        self.Question.brackets_color = Colours.GREY.value
        self.List.selection_color = Colours.CLAY.value
        self.List.selection_cursor = "❯"

# Checking whether there's only one choice in prompt 
# without losing performance is serious business at mov-cli. ~ Goldy 2024
def is_it_just_one_choice(choices: Iterable[T]) -> Tuple[bool, List[T] | Generator[T, Any, None]]:

    if isinstance(choices, types.GeneratorType):

        choices, unwounded_iterable = itertools.tee(choices) # nuh uh uh uh, we ain't wasting memory and speed.

        did_iter = False

        for index, _ in enumerate(choices):
            did_iter = True

            if index >= 1:
                return False, unwounded_iterable

        if did_iter is False:
            return False, unwounded_iterable

        return True, unwounded_iterable

    if len(choices) == 1:
        return True, choices

    return False, choices

def prompt(text: str, choices: List[T] | Generator[T, Any, None], display: Callable[[T], str], fzf_enabled: bool) -> T | None:
    """Prompt the user to pick from a list choices."""
    choice_picked = None

    is_just_one, choices = is_it_just_one_choice(choices)

    if is_just_one is True:
        logger.debug("Skipping prompt as there is only a single choice to choose from...")
        return next(choices) if isinstance(choices, itertools._tee) else choices[0]

    # silence the global logger so it doesn't mess with fzf or inquirer's output.
    previous_logger_level = mov_cli_logger.level
    mov_cli_logger.setLevel(logging.CRITICAL)

    choices, unwounded_choices = itertools.tee(choices)

    if fzf_enabled:
        logger.debug("Launching fzf...")
        # We pass this in as a generator to take advantage of iterfzf's streaming capabilities.
        # You can find that explained as the second bullet point here: https://github.com/dahlia/iterfzf#key-features
        choice_picked = iterfzf(
            iterable = ((display(choice), choice) for choice in choices), 
            prompt = text + ": ", 
            ansi = True
        )

    else:
        logger.debug("Launching inquirer (fallback ui)...")
        inquirer_result = inquirer.prompt(
            questions = [inquirer.List("choices", message = text, choices = [display(x) for x in choices])], 
            theme = MovCliTheme()
        )

        if inquirer_result is not None:
            choice_picked = inquirer_result["choices"]

    # restore the logger
    mov_cli_logger.setLevel(previous_logger_level)

    # Using this to remove ansi colours returned in the picked choice.
    ansi_remover = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    if choice_picked is None:
        return None

    for choice in unwounded_choices:

        if ansi_remover.sub('', choice_picked) == ansi_remover.sub('', display(choice)):
            return choice

    return None

def greetings() -> Tuple[Literal["Good Morning", "Good Afternoon", "Good Evening", "Good Night"], str]:
    now = datetime.now()
    user_name = random.choice(
        ("buddy", "comrade", "co-worker", "human", "companion", "specimen")
    )

    p = now.strftime("%p")
    i = int(now.strftime("%I"))

    try:
        user_name = user_name if what_platform() in ["Android", "iOS"] else getpass.getuser()
    except Exception as e:  # NOTE: Apparently an exception is raised but they don't tell us what exception :(
        mov_cli_logger.debug(
            "getpass couldn't get the user name so a random one is being returned. "
            f"\nError >> {e}"
        )

    greeting = None

    if p == "AM":
        if i <= 6 or i == 12:
            greeting = "Good Night"
        else:
            greeting = "Good Morning"
    else:
        if i <= 5:
            greeting = "Good Afternoon"
        elif i > 5 and i <= 8:
            greeting = "Good Evening"
        elif i > 8:
            greeting = "Good Night"

    return greeting, user_name

# This function below is inspired by animdl: https://github.com/justfoolingaround/animdl
def welcome_msg(
    plugins: Dict[str, str], 
    check_for_updates: bool = False, 
    display_tip: bool = False, 
    display_version: bool = False
) -> str:
    """Returns cli welcome message."""
    now = datetime.now()
    adjective = random.choice(
        ("gorgeous", "wonderful", "beautiful", "magnificent")
    )

    random_tips_path = Path(os.path.split(__file__)[0]).joinpath("random_tips.json")

    greeting, user_name = greetings()

    text = f"\n{greeting}, {Colours.ORANGE.apply(user_name)}."
    text += now.strftime(
        f"\n    It's {Colours.BLUE}%I:%M %p {Colours.RESET}on a {Colours.PURPLE}{adjective} {Colours.PINK_GREY}%A! {Colours.RESET}"
    )

    if display_tip and display_version is False:

        if random.randint(0, 1) == 0:
            text += f"\n\n- {Colours.BLUE}Hint: {Colours.RESET}mov-cli {Colours.PINK_GREY}-s films {Colours.ORANGE}mr.robot{Colours.RESET}" \
                f"\n- {Colours.BLUE}Hint: {Colours.RESET}mov-cli {Colours.PINK_GREY}-s anime {Colours.ORANGE}chuunibyou demo take on me{Colours.RESET}"

        else:
            random_tips_json: List[str] = json.load(random_tips_path.open("r")) # TODO: This should be cached after the caching system is implemented.
            random_tip = random.choice(random_tips_json)

            text += f"\n\n- {Colours.ORANGE}TIP: {Colours.RESET}{random_tip}"

    if display_version is True:
        text += f"\n\n{Colours.CLAY}-> {Colours.RESET}Version: {Colours.BLUE}{mov_cli.__version__}{Colours.RESET}"

    if check_for_updates:

        if update_available():
            text += f"\n\n {Colours.PURPLE}ツ {Colours.ORANGE}An update is available! --> {Colours.RESET}pip install mov-cli -U"

        plugin_needs_updating, plugins_to_update = plugin_update_available(plugins)

        if plugin_needs_updating:
            text += f"\n\n {Colours.ORANGE}|˶˙ᵕ˙ )ﾉﾞ {Colours.GREEN}Some plugins need updating! --> {Colours.RESET}pip install {' '.join(plugins_to_update)} -U"

    return text + "\n"