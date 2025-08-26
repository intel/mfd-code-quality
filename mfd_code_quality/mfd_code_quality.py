# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Main module."""

import logging
from collections import namedtuple


logger = logging.getLogger("mfd-code-quality.general")

PathHelpTuple = namedtuple("PathHelpTuple", "path, help")

AVAILABLE_CHECKS = {
    "mfd-code-standard": PathHelpTuple(
        path="mfd_code_quality.code_standard.checks:run_checks",
        help="Check code standard using Ruff (format, check) or flake8. Depending on what is available.",
    ),
    "mfd-code-format": PathHelpTuple(
        path="mfd_code_quality.code_standard.formats:format_code",
        help="Run Ruff linter and formatter.",
    ),
    "mfd-import-tests": PathHelpTuple(
        path="mfd_code_quality.testing_utilities.import_tests:run_checks",
        help="Run import tests of each Python file to check import problems.",
    ),
    "mfd-unit-tests": PathHelpTuple(
        path="mfd_code_quality.testing_utilities.unit_tests:run_unit_tests",
        help="Run unittests without coverage check.",
    ),
    "mfd-unit-tests-with-coverage": PathHelpTuple(
        path="mfd_code_quality.testing_utilities.unit_tests:run_unit_tests_with_coverage",
        help="Run unittests and check if new code coverage is reaching the threshold (80%).",
    ),
    "mfd-system-tests": PathHelpTuple(
        path="mfd_code_quality.testing_utilities.system_tests:run_checks", help="Run system tests."
    ),
    "mfd-all-checks": PathHelpTuple(
        path="mfd_code_quality.mfd_code_quality:run_all_checks",
        help="Run all available checks.",
    ),
    "mfd-help": PathHelpTuple(path="mfd_code_quality.mfd_code_quality:log_help_info", help="Log available commands."),
}


def log_help_info() -> None:
    """Log information about available commands."""
    from mfd_code_quality.utils import set_up_logging

    set_up_logging()

    checks_help = "\n".join([f"{cmd:<30}: {details.help}" for cmd, details in AVAILABLE_CHECKS.items()])
    logger.info(
        f"Available commands:\n\n{checks_help}\n\n"
        "Arguments available for all commands:\n"
        "-p / --project-dir <path>     : Specify root directory to run checks in. "
        "Current working directory is a default.\n"
        "-v / --verbose                : Enable verbose logging."
    )


def run_all_checks() -> bool:
    """Run all available checks."""
    from mfd_code_quality.code_standard.checks import _get_available_code_standard_module
    from mfd_code_quality.code_standard.configure import create_config_files, delete_config_files
    from .code_standard.checks import _run_code_standard_tests as code_standard_check
    from .testing_utilities.import_tests import _run_import_tests as import_tests_check
    from .testing_utilities.system_tests import _run_system_tests as system_tests_check
    from .testing_utilities.unit_tests import _run_unit_tests as unit_tests_with_coverage_check

    code_standard_module = _get_available_code_standard_module()
    if code_standard_module == "ruff":
        create_config_files()
    result = all(
        [
            code_standard_check(with_configs=False),
            import_tests_check(),
            system_tests_check(),
            unit_tests_with_coverage_check(compare_coverage=True, with_configs=False),
        ]
    )
    if code_standard_module == "ruff":
        delete_config_files()

    logger.info("All checks PASSED." if result else "Some checks FAILED.")
    return result
