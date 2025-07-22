# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Module for ruff linter and formatter executors."""

import logging
import sys
from subprocess import run

from mfd_code_quality.code_standard.configure import create_config_files, delete_config_files
from mfd_code_quality.utils import get_root_dir

logger = logging.getLogger("mfd-code-quality.code_standard")


def _run_linter() -> bool:
    """
    Run ruff linter with format.

    :return: True if ruff check did not find any issues, False - otherwise.
    """
    logger.info("Running 'ruff check --fix'...")
    ruff_run_outcome = run(
        (sys.executable, "-m", "ruff", "check", "--fix"), capture_output=True, text=True, cwd=get_root_dir()
    )
    logger.info(f"Output: {ruff_run_outcome.stdout.strip()}")
    return ruff_run_outcome.returncode == 0


def _run_formatter() -> bool:
    """
    Run ruff linter with format.

    :return: True if ruff check did not find any issues, False - otherwise.
    """
    logger.info("Running 'ruff format'...")
    ruff_run_outcome = run((sys.executable, "-m", "ruff", "format"), capture_output=True, text=True, cwd=get_root_dir())
    logger.info(f"Output: {ruff_run_outcome.stdout.strip()}")
    return ruff_run_outcome.returncode == 0


def format_code() -> None:
    """Run linter and formatter."""
    create_config_files()
    statuses = [_run_linter(), _run_formatter()]
    delete_config_files()
    sys.exit(not all(statuses))
