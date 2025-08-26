# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""General utilities."""

import logging
import os
import sys
from argparse import ArgumentParser, Namespace
from functools import lru_cache
from pathlib import Path
from subprocess import run

from setuptools import find_packages

from mfd_code_quality.log_formatter import CustomLogFormatter

logger = logging.getLogger("mfd-code-quality.utils")


class CustomFilter(logging.Filter):
    """Custom filter to check if log message is coming from this module."""

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
        """Check if log message is coming from this module."""
        return "mfd-code-quality" in record.name


def set_up_basic_config(log_level: int = logging.INFO) -> None:
    """
    Set up basic config of logging.

    The `%(msg)s` placeholder is intentionally omitted from the format string because
    the `CustomLogFormatter` automatically appends it with proper indentations.

    :param log_level: Level to be set in config as the lowest acceptable value.
    """
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(name)13.13s | %(levelname)4.4s | ",
        datefmt="%H:%M:%S",
    )


@lru_cache()
def set_up_logging() -> None:
    """Set up logging to print only logs from this file."""
    set_up_basic_config(log_level=logging.DEBUG if get_parsed_args().verbose else logging.INFO)
    root_stream_handler = next(
        (handler for handler in logging.getLogger().handlers if isinstance(handler, logging.StreamHandler)), None
    )
    if root_stream_handler is not None:
        root_stream_handler.addFilter(CustomFilter())
        root_stream_handler.setStream(sys.stdout)
        root_stream_handler.setFormatter(CustomLogFormatter(root_stream_handler.formatter))


@lru_cache()
def get_parsed_args() -> Namespace:
    """Get parsed command line arguments."""
    parser = ArgumentParser()
    parser.add_argument(
        "-p", "--project-dir", help="Path to tested project, if not given current directory will be used.", type=str
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")
    return parser.parse_args()


@lru_cache()
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


def get_package_name(root_dir: str | Path | None = None) -> str:
    """
    Get Python package name.

    :return: Package name, example "mfd_network_adapter", "pydantic", ...
    :raise Exception: When project folder not found
    """
    # *.* will exclude all subpackages as we are looking for root package name
    root_dir = root_dir or get_root_dir()
    packages = find_packages(where=root_dir, exclude=["tests", "tests.*", "*.*"])
    if not packages:
        raise Exception(f"No Python package was found in {root_dir}!")

    if len(packages) > 1:
        logger.warning(
            f"Multiple Python packages found in {root_dir}: {packages}.\n"
            "Support for such repositories is not implemented yet. If needed don't hesitate to submit GH issue.\n"
            f"Using first package: {packages[0]}."
        )

    return packages[0]
