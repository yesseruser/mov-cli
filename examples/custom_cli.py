# This is a simple example on how to use mov-cli as a library.
# This script requires the mov-cli-youtube plugin to be installed!
#
# pip install mov-cli-youtube -U

import time

from mov_cli import prompt
from mov_cli.config import Config
from mov_cli.players import PLAYER_TABLE
from mov_cli.http_client import HTTPClient
from mov_cli.utils import EpisodeSelector, what_platform

from mov_cli_youtube.yt_dlp import YTDlpScraper

WELCOME_MESSAGE = f"Hello and welcome to my custom mov-cli script!\n\n" \
    "What would you like to watch from YouTube?\n"

if __name__ == "__main__":
    print(WELCOME_MESSAGE)

    time.sleep(1)

    query = input("Enter your query -> ")

    config = Config()
    http_client = HTTPClient()
    platform = what_platform()

    scraper = YTDlpScraper(
        config = config,
        http_client = http_client
    )

    print("I'm searching... ⚆ _ ⚆")
    search_results = scraper.search(query)

    choice = prompt(
        text = "Which youtube video would you like to watch?",
        choices = search_results,
        display = lambda x: x.title,
        fzf_enabled = config.fzf_enabled
    )

    if choice is None:
        print("No video was selected. :(")

    print("Scrapping that... ◉_◉")
    media = scraper.scrape(choice, EpisodeSelector())

    player_class = PLAYER_TABLE["mpv"]

    player = player_class(platform = platform)

    popen = player.play(media)

    print("I'm playing :)")

    popen.wait()