# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Main module."""

import logging
from collections import namedtuple


logger = logging.getLogger(__name__)

PathHelpTuple = namedtuple("PathHelpTuple", "path, help")

AVAILABLE_CHECKS = {
    "mfd-code-standard": PathHelpTuple(
        path="mfd_code_quality.code_standard.checks:run_checks",
        help="Run code standard test using ruff (format, check) or flake8. Depending on what is available.",
    ),
    "mfd-import-testing": PathHelpTuple(
        path="mfd_code_quality.testing_utilities.import_testing:run_checks",
        help="Run import testing of each Python file to check import problems.",
    ),
    "mfd-system-tests": PathHelpTuple(
        path="mfd_code_quality.testing_utilities.system_tests:run_checks", help="Run system tests."
    ),
    "mfd-unit-tests": PathHelpTuple(
        path="mfd_code_quality.testing_utilities.unit_tests:run_unit_tests",
        help="Run unittests, print actual coverage, but don't check its value.",
    ),
    "mfd-unit-tests-with-coverage": PathHelpTuple(
        path="mfd_code_quality.testing_utilities.unit_tests:run_unit_tests_with_coverage",
        help="Run unittests and check if diff coverage (new code coverage) is reaching the threshold.",
    ),
    "mfd-all-checks": PathHelpTuple(
        path="mfd_code_quality.mfd_code_quality:run_all_checks",
        help="Run all available checks.",
    ),
    "mfd-format-code": PathHelpTuple(
        path="mfd_code_quality.code_standard.formats:format_code",
        help="Run linter format and formatter.",
    ),
    "mfd-help": PathHelpTuple(path="mfd_code_quality.mfd_code_quality:log_help_info", help="Log available commands."),
    "mfd-configure-code-standard": PathHelpTuple(
        path="mfd_code_quality.code_standard.configure:configure_code_standard",
        help="Configure repository for code standard.\n"
        "\t\t\t\t\tRun this command before running any code standard check (mfd-code-standard).\n"
        "\t\t\t\t\tActions performed:\n"
        "\t\t\t\t\t- copy .pre-commit-config.yaml to project's root directory\n"
        "\t\t\t\t\t- create pyproject.toml with configurations defined in generic_pyproject.txt and custom "
        "pyproject.toml file located in target repository.\n"
        "\t\t\t\t\t- create ruff.toml with configurations defined in generic_ruff.txt and custom "
        "ruff.toml file located in target repository.\n"
        "\t\t\t\t\tGenerated configurations should include ruff, code coverage and semantic release configurations.\n"
        "\t\t\t\t\t- install pre-commit",
    ),
    "mfd-create-config-files": PathHelpTuple(
        path="mfd_code_quality.code_standard.configure:create_config_files",
        help="Create config files pyproject.toml and ruff.toml.\n"
        "\t\t\t\t\tRun this command before running any code standard check (mfd-code-standard).\n"
        "\t\t\t\t\tActions performed:\n"
        "\t\t\t\t\t- create pyproject.toml with configurations defined in generic_pyproject.txt and custom "
        "pyproject.toml file located in target repository.\n"
        "\t\t\t\t\t- create ruff.toml with configurations defined in generic_ruff.txt and custom "
        "ruff.toml file located in target repository.\n"
        "\t\t\t\t\tGenerated configurations should include ruff, code coverage and semantic release configurations.\n",
    ),
    "mfd-delete-config-files": PathHelpTuple(
        path="mfd_code_quality.code_standard.configure:delete_config_files",
        help="Delete config files pyproject.toml and ruff.toml.\n",
    ),
}


def log_help_info() -> None:
    """Log information about available commands."""
    from mfd_code_quality.utils import set_up_logging

    set_up_logging()

    checks_help = "\n".join([f"\t{cmd:<30}: {details.help}" for cmd, details in AVAILABLE_CHECKS.items()])
    logger.info(
        f"Available commands:\n\n{checks_help}\n\n"
        "Each command can be combined with --project-dir argument. "
        "If not specified current working directory will be used."
    )


def run_all_checks() -> bool:
    """Run all available checks."""
    from mfd_code_quality.code_standard.checks import _get_available_code_standard_module
    from mfd_code_quality.code_standard.configure import create_config_files, delete_config_files
    from .code_standard.checks import _run_code_standard_tests as code_standard_check
    from .testing_utilities.import_testing import _run_import_tests as import_testing_check
    from .testing_utilities.system_tests import _run_system_tests as system_tests_check
    from .testing_utilities.unit_tests import _run_unit_tests as unit_tests_with_coverage_check

    code_standard_module = _get_available_code_standard_module()
    if code_standard_module == "ruff":
        create_config_files()
    result = all(
        [
            code_standard_check(with_configs=False),
            import_testing_check(),
            system_tests_check(),
            unit_tests_with_coverage_check(compare_coverage=True, with_configs=False),
        ]
    )
    if code_standard_module == "ruff":
        delete_config_files()
    return result
