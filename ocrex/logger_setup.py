"""
Logger setup module for OCRex.
This module configures the logging system using Rich's RichHandler
to provide colored and formatted terminal output.
It ensures that logging is both informative and
user-friendly—critical for production-grade applications.
"""

import logging
from rich.logging import RichHandler


def setup_logger(verbose: bool = False):
    """
    Configures the logging for OCRex.

    Args:
        verbose (bool): If True, the logger is set to DEBUG
        level for detailed output.

        Otherwise, it defaults to INFO level.
    """
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )
