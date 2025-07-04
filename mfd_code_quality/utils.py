# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""General utilities."""

import logging
import os
import sys

from argparse import ArgumentParser, Namespace
from subprocess import run

from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)


class CustomFilter(logging.Filter):
    """Custom filter to check if log message is coming from this module."""

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
        """Check if log message is coming from this module."""
        return __name__.split(".", maxsplit=1)[0] in record.name


def set_up_basic_config(log_level: int = logging.INFO) -> None:
    """
    Set up basic config of logging.

    :param log_level: Level to be set in config as the lowest acceptable value.
    """
    logging.basicConfig(level=log_level, format="%(asctime)s | %(name)35.35s | %(levelname)5.5s | %(msg)s")


def set_up_logging() -> None:
    """Set up logging to print only logs from this file."""
    set_up_basic_config(log_level=logging.DEBUG)
    root_stream_handler = next(
        (handler for handler in logging.getLogger().handlers if isinstance(handler, logging.StreamHandler)), None
    )
    if root_stream_handler is not None:
        root_stream_handler.addFilter(CustomFilter())
        root_stream_handler.setStream(sys.stdout)


@lru_cache()
def get_parsed_args() -> Namespace:
    """Get parsed command line arguments."""
    parser = ArgumentParser()
    parser.add_argument(
        "-p", "--project-dir", help="Path to tested project, if not given current directory will be used.", type=str
    )
    return parser.parse_args()


def get_root_dir() -> Path:
    """Get root dir from cmd argument or current working directory."""
    return Path(get_parsed_args().project_dir if get_parsed_args().project_dir else os.getcwd())


def set_cwd() -> None:
    """Set current working directory and add it to the path."""
    os.chdir(get_root_dir())
    sys.path.insert(0, str(get_root_dir()))


def _install_packages(path_to_req: str) -> None:
    """
    Install packages from the list.

    :param path_to_req: Path to requirements file.
    """
    output = run((sys.executable, "-m", "pip", "install", "-r", path_to_req), capture_output=True, text=True)
    logger.debug(f"stdout: {output.stdout}")
    logger.debug(f"stderr: {output.stderr}")
