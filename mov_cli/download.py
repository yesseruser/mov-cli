from __future__ import annotations
from typing import TYPE_CHECKING
import subprocess
import unicodedata
import os
import importlib.util as iu

__all__ = ("Download",)

if TYPE_CHECKING:
    from .config import Config
    from .media import Series, Movie

from .logger import mov_cli_logger
from devgoldyutils import LoggerAdapter

class Download():
    def __init__(self, config: Config) -> None:
        self.config = config
        self.logger = LoggerAdapter(mov_cli_logger, "Downloader")

    def download(self, media: Series | Movie, subtitles: str = None) -> subprocess.Popen:
        title = unicodedata.normalize('NFKD', media.display_name).encode('ascii', 'ignore').decode('ascii') # normalize title

        yt_dlp = None

        if self.config.use_yt_dlp:
            yt_dlp = iu.find_spec("yt_dlp")

        file = os.path.join(self.config.download_location, title + ".mp4")

        if yt_dlp and not media.audio_url:
            import yt_dlp

            ydl_options = {
                "outtmpl": file,
                "quiet": not self.config.debug,
                "http_headers": {"Referer": media.referrer}
            }

            with yt_dlp.YoutubeDL(ydl_options) as ydl:
                ydl.download(media.url)

            return None

        else:
            self.logger.debug("Using FFmpeg as the URL was either not a m3u8 or yt-dlp is not installed")
            

            args = [ # TODO: Check if url is a m3u8 if not use aria2
                "ffmpeg",
                "-n",
                "-headers",
                f"Referer: {media.referrer}",
                "-i",
                media.url,
            ]

            if media.audio_url:
                args.extend(["-i", media.audio_url])

            if subtitles:
                args.extend(["-vf", f"subtitle={subtitles}"])

            args.extend(["-c", "copy", file])

            return subprocess.Popen(args)

