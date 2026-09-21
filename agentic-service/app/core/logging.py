import logging
import sys

from app.core.config import settings


def setup_logging() -> None:
    """
    Configure application-wide logging.

    This function is safe to call more than once.
    """

    log_level = getattr(
        logging,
        settings.log_level.upper(),
        logging.INFO,
    )

    logging.basicConfig(
        level=log_level,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        stream=sys.stdout,
        force=True,
    )


def get_logger(name: str) -> logging.Logger:
    """
    Return a logger for the given module.
    """

    return logging.getLogger(name)