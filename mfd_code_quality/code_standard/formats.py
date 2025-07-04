# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Module for ruff linter and formatter executors."""

import logging
import sys
from subprocess import run

from mfd_code_quality.code_standard.configure import create_config_files, delete_config_files
from mfd_code_quality.utils import get_root_dir

logger = logging.getLogger(__name__)


def _run_linter() -> bool:
    """
    Run ruff linter with format.

    :return: True if ruff check did not find any issues, False - otherwise.
    """
    logger.info("Checking 'ruff check --fix'...")
    ruff_run_outcome = run((sys.executable, "-m", "ruff", "check", "--fix"), cwd=get_root_dir())
    return ruff_run_outcome.returncode == 0


def _run_formatter() -> bool:
    """
    Run ruff linter with format.

    :return: True if ruff check did not find any issues, False - otherwise.
    """
    logger.info("Checking 'ruff format'...")
    ruff_run_outcome = run((sys.executable, "-m", "ruff", "format"), cwd=get_root_dir())
    return ruff_run_outcome.returncode == 0


def format_code() -> None:
    """Run linter and formatter."""
    create_config_files()
    logger.info("#" * 30)
    logger.info("Running ruff linter and formatter...")
    statuses = [_run_linter(), _run_formatter()]
    logger.info("End of ruff linter and formatter...")
    logger.info("#" * 30)
    delete_config_files()
    if not all(statuses):
        sys.exit(1)
    sys.exit(0)
