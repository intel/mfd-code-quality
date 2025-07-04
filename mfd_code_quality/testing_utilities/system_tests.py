# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""System tests utilities."""

import contextlib
import logging
import shutil
import sys

import pytest

from .consts import PYTEST_OK_STATUSES
from ..utils import get_root_dir, set_up_logging, set_cwd

logger = logging.getLogger(__name__)


def _run_system_tests() -> bool:
    """
    Run system tests.

    :return: True if all tests passed, False otherwise.
    """
    set_up_logging()
    set_cwd()

    with contextlib.suppress(FileNotFoundError):
        shutil.rmtree(get_root_dir() / ".pytest_cache")

    params = [str(get_root_dir() / "tests" / "system")]
    testing_run_outcome = pytest.main(args=params)

    return_val = testing_run_outcome in PYTEST_OK_STATUSES
    if return_val:
        logger.info("System tests check passed")

    return return_val


def run_checks() -> None:
    """Run system tests."""
    return_val = _run_system_tests()
    sys.exit(0 if return_val else 1)
