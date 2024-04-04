from __future__ import annotations

import httpx
from packaging import version
from devgoldyutils import LoggerAdapter, Colours

import mov_cli
from ..logger import mov_cli_logger

__all__ = ("update_available",)

logger = LoggerAdapter(mov_cli_logger, prefix = Colours.GREEN.apply("version"))

def update_available() -> bool:
    logger.debug("Checking if mov-cli needs updating...")

    update_fail_msg = "Failed to check for mov-cli update!"

    try:
        response = httpx.get("https://pypi.org/pypi/mov-cli/json")
    except httpx.HTTPError as e:
        logger.warning(update_fail_msg + f" Error: {e}")
        return False

    if response.status_code >= 400:
        logger.warning(update_fail_msg + f" Response: {response}")
        return False

    pypi_json = response.json()
    pypi_version: str = pypi_json["info"]["version"]

    if version.parse(pypi_version) > version.parse(mov_cli.__version__):
        return True

    return False