# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Unit tests utilities."""

import logging
import shutil
import sys

import pytest
from coverage import Coverage
from coverage.exceptions import NoDataError

from mfd_code_quality.code_standard.configure import delete_config_files, create_config_files
from mfd_code_quality.coverage.consts import COVERAGE_XML_FILE, COVERAGE_JSON_FILE
from mfd_code_quality.coverage.utils import (
    pkg_to_include_in_cov,
    coverage_section,
    log_module_coverage,
    is_diff_coverage_threshold_reached,
)
from mfd_code_quality.testing_utilities.consts import PYTEST_OK_STATUSES
from mfd_code_quality.utils import get_root_dir, set_cwd, set_up_logging

logger = logging.getLogger(__name__)


def _run_unit_tests(compare_coverage: bool = False, with_configs: bool = True) -> bool:
    """
    Run unit tests and compare coverage data if requested.

    :param compare_coverage: Should we compare coverage
    :param with_configs: Should we create configuration files before running checks.
    :return: True if tests completed successfully and (if requested) coverage threshold met
    """
    set_up_logging()
    set_cwd()
    if with_configs:
        create_config_files()
    root_dir = get_root_dir()

    (root_dir / ".coverage").unlink(missing_ok=True)  # sqlite db created by coverage
    (root_dir / COVERAGE_XML_FILE).unlink(missing_ok=True)
    (root_dir / COVERAGE_JSON_FILE).unlink(missing_ok=True)
    shutil.rmtree(root_dir / ".pytest_cache", ignore_errors=True)

    # we don't need to check cov of template modules
    if (root_dir / "{{cookiecutter.project_slug}}").exists():
        params = [str(root_dir / "tests" / "unit")]
        return pytest.main(args=params) in PYTEST_OK_STATUSES

    package_name = pkg_to_include_in_cov()
    unit_tests_path = str(root_dir / "tests" / "unit")
    params = ["-n 5", f"--cov={package_name}", unit_tests_path]

    cov = Coverage(source_pkgs=[package_name])
    with cov.collect():
        testing_run_outcome = pytest.main(args=params)

    return_val = testing_run_outcome in PYTEST_OK_STATUSES

    with coverage_section():
        try:
            cov.load()
            cov.json_report(outfile=COVERAGE_JSON_FILE)
            log_module_coverage()
        except NoDataError:
            logger.warning("[Coverage] Coverage did not collect any data. Probably there are no unit tests.")
            return return_val

        if compare_coverage:
            cov.xml_report(outfile=COVERAGE_XML_FILE)
            if not is_diff_coverage_threshold_reached():
                return False
        else:
            logger.info(
                "[Coverage] Coverage will NOT be compared to threshold as unit tests without coverage were requested."
            )

    if return_val:
        logger.info("Unit tests check passed")
    if with_configs:
        delete_config_files()
    return return_val


def run_unit_tests(with_configs: bool = False) -> None:
    """
    Run unit tests without coverage comparison.

    :param with_configs: Should we create configuration files before running checks.
    """
    sys.exit(0 if _run_unit_tests(compare_coverage=False, with_configs=with_configs) else 1)


def run_unit_tests_with_coverage(with_configs: bool = False) -> None:
    """
    Run unit tests with coverage comparison.

    :param with_configs: Should we create configuration files before running checks.
    """
    sys.exit(0 if _run_unit_tests(compare_coverage=True, with_configs=with_configs) else 1)
