import logging
import warnings
from devgoldyutils import add_custom_handler, Colours

__all__ = (
    "mov_cli_logger",
    "warn_deprecation"
)

mov_cli_logger = add_custom_handler(
    logger = logging.getLogger(Colours.WHITE.apply("mov_cli")), 
    level = logging.INFO
)

def warn_deprecation(message: str, stacklevel: int = 3) -> None:
    warnings.warn(
        message,
        category = DeprecationWarning,
        stacklevel = stacklevel + 1
    )