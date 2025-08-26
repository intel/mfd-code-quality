# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Code standards utilities."""

import logging
import sys
from subprocess import run

from .configure import delete_config_files, create_config_files
from ..utils import get_root_dir, set_up_logging, set_cwd

logger = logging.getLogger("mfd-code-quality.code_standard")


def _test_flake8() -> bool:
    """
    Run flake8 tests.

    :return: True if test completed successfully, False - otherwise.
    """
    flake_run_outcome = run((sys.executable, "-m", "flake8"), cwd=get_root_dir())
    return flake_run_outcome.returncode == 0


def _test_ruff_format() -> bool:
    """
    Run ruff format check.

    :return: True if there is nothing to format, False - otherwise.
    """
    logger.info("Checking 'ruff format --check'...")
    ruff_format_outcome = run(
        (sys.executable, "-m", "ruff", "format", "--check"), capture_output=True, text=True, cwd=get_root_dir()
    )
    logger.info(f"Output: {ruff_format_outcome.stdout.strip()}")
    return ruff_format_outcome.returncode == 0


def _test_ruff_check() -> bool:
    """
    Run ruff linter check.

    :return: True if ruff check did not find any issues, False - otherwise.
    """
    logger.info("Checking 'ruff check'...")
    ruff_run_outcome = run((sys.executable, "-m", "ruff", "check"), capture_output=True, text=True, cwd=get_root_dir())
    logger.info(f"Output: {ruff_run_outcome.stdout.strip()}")
    return ruff_run_outcome.returncode == 0


def _get_available_code_standard_module() -> str:
    """
    Get available code standard module which is installed in python.

    It will be either flake8 or ruff.

    :return: flake8 or ruff
    :raises Exception: When no code standard module is available
    """
    code_standard_modules = ["ruff", "flake8"]
    pip_list = run((sys.executable, "-m", "pip", "list"), capture_output=True, text=True, cwd=get_root_dir())
    for code_standard_module in code_standard_modules:
        if f"{code_standard_module} " in pip_list.stdout:
            logger.info(f"{code_standard_module.capitalize()} will be used for code standard check.")
            return code_standard_module

    raise Exception("No code standard module is available! [flake8 or ruff]")


def _run_code_standard_tests(with_configs: bool = True) -> bool:
    """
    Run code standard tests.

    :param with_configs: Should we create configuration files before running checks.
    :return: True if all tests passed, False otherwise.
    """
    set_up_logging()
    set_cwd()
    code_standard_module = None
    try:
        results = []
        code_standard_module = _get_available_code_standard_module()
        if code_standard_module == "ruff":
            if with_configs:
                logger.debug("Prepare configuration files required for checks.")
                create_config_files()
            results.append(_test_ruff_format())
            results.append(_test_ruff_check())
        elif code_standard_module == "flake8":
            results.append(_test_flake8())

        return_val = all(results)
        if return_val:
            message = "Code standard check PASSED."
        else:
            if code_standard_module == "ruff":
                logger.info(
                    "Ruff check was called correctly, however check failed.\n"
                    "For fixing code standard call 'mfd-code-format' first.\n"
                    "If you want to see more details what is wrong, call 'ruff format --diff'.\n"
                )
            message = "Code standard check FAILED."
        logger.info(message)
    finally:
        if code_standard_module == "ruff" and with_configs:
            logger.debug("Delete configuration files.")
            delete_config_files()

    return return_val


def run_checks(with_configs: bool = True) -> None:
    """
    Run code standard tests.

    :param with_configs: Should we create configuration files before running checks.
    """
    return_val = _run_code_standard_tests(with_configs)

    sys.exit(0 if return_val else 1)
