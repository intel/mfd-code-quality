# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Test testing_utilities.unit_tests."""

import sys

import pytest
from unittest.mock import patch

from coverage.exceptions import NoDataError

from mfd_code_quality.testing_utilities.unit_tests import _run_unit_tests, run_unit_tests, run_unit_tests_with_coverage


@pytest.fixture
def mock_dependencies():
    with (
        patch("mfd_code_quality.testing_utilities.unit_tests.set_up_logging") as mock_set_up_logging,
        patch("mfd_code_quality.testing_utilities.unit_tests.set_cwd") as mock_set_cwd,
        patch("mfd_code_quality.testing_utilities.unit_tests.get_root_dir") as mock_get_root_dir,
        patch("mfd_code_quality.testing_utilities.unit_tests.pkg_to_include_in_cov") as mock_pkg_to_include_in_cov,
        patch("mfd_code_quality.testing_utilities.unit_tests.Coverage") as mock_Coverage,
        patch("mfd_code_quality.testing_utilities.unit_tests.coverage_section") as mock_coverage_section,
        patch("mfd_code_quality.testing_utilities.unit_tests.log_module_coverage") as mock_log_module_coverage,
        patch(
            "mfd_code_quality.testing_utilities.unit_tests.is_diff_coverage_threshold_reached"
        ) as mock_is_diff_coverage_threshold_reached,
        patch("mfd_code_quality.testing_utilities.unit_tests.pytest.main") as mock_pytest_main,
    ):
        yield {
            "mock_set_up_logging": mock_set_up_logging,
            "mock_set_cwd": mock_set_cwd,
            "mock_get_root_dir": mock_get_root_dir,
            "mock_pkg_to_include_in_cov": mock_pkg_to_include_in_cov,
            "mock_Coverage": mock_Coverage,
            "mock_coverage_section": mock_coverage_section,
            "mock_log_module_coverage": mock_log_module_coverage,
            "mock_is_diff_coverage_threshold_reached": mock_is_diff_coverage_threshold_reached,
            "mock_pytest_main": mock_pytest_main,
        }


def test_run_unit_tests_successfully(mock_dependencies):
    mock_dependencies["mock_pkg_to_include_in_cov"].return_value = "test_package"
    mock_dependencies["mock_pytest_main"].return_value = 0  # Simulate pytest success
    assert _run_unit_tests(compare_coverage=False, with_configs=False) is True


def test_run_unit_tests_with_coverage_with_configs_successfully(mock_dependencies, mocker):
    mock_dependencies["mock_pkg_to_include_in_cov"].return_value = "test_package"
    mock_dependencies[
        "mock_get_root_dir"
    ].return_value.__truediv__.return_value.__truediv__.return_value = "root_dir/tests/unit"
    mock_dependencies["mock_get_root_dir"].return_value.__truediv__.return_value.exists.return_value = False
    mock_dependencies["mock_pytest_main"].return_value = 0
    mock_dependencies["mock_is_diff_coverage_threshold_reached"].return_value = True
    mocker.patch("mfd_code_quality.testing_utilities.unit_tests.create_config_files")
    mocker.patch("mfd_code_quality.testing_utilities.unit_tests.delete_config_files")
    assert _run_unit_tests(compare_coverage=True, with_configs=True) is True
    mock_dependencies["mock_pytest_main"].assert_called_once_with(
        args=["-n 5", "--cov=test_package", "root_dir/tests/unit"]
    )


def test_run_unit_tests_with_coverage_successfully(mock_dependencies):
    mock_dependencies["mock_pkg_to_include_in_cov"].return_value = "test_package"
    mock_dependencies[
        "mock_get_root_dir"
    ].return_value.__truediv__.return_value.__truediv__.return_value = "root_dir/tests/unit"
    mock_dependencies["mock_get_root_dir"].return_value.__truediv__.return_value.exists.return_value = False
    mock_dependencies["mock_pytest_main"].return_value = 0
    mock_dependencies["mock_is_diff_coverage_threshold_reached"].return_value = True

    assert _run_unit_tests(compare_coverage=True, with_configs=False) is True
    mock_dependencies["mock_pytest_main"].assert_called_once_with(
        args=["-n 5", "--cov=test_package", "root_dir/tests/unit"]
    )


def test_run_unit_tests_with_coverage_threshold_not_met(mock_dependencies):
    mock_dependencies["mock_get_root_dir"].return_value.__truediv__.return_value.exists.return_value = False
    mock_dependencies["mock_pkg_to_include_in_cov"].return_value = "test_package"
    mock_dependencies["mock_is_diff_coverage_threshold_reached"].return_value = False
    assert _run_unit_tests(compare_coverage=True, with_configs=False) is False


def test_run_unit_tests_no_coverage_data(mock_dependencies):
    mock_dependencies["mock_pkg_to_include_in_cov"].return_value = "test_package"
    mock_dependencies["mock_get_root_dir"].return_value.__truediv__.return_value.exists.return_value = False
    mock_dependencies["mock_pytest_main"].return_value = 0
    mock_dependencies["mock_Coverage"].return_value.load.side_effect = NoDataError
    assert _run_unit_tests(compare_coverage=True, with_configs=False) is True


def test_run_unit_tests_failed_no_coverage_data(mock_dependencies):
    mock_dependencies["mock_get_root_dir"].return_value.__truediv__.return_value.exists.return_value = False
    mock_dependencies["mock_pkg_to_include_in_cov"].return_value = "test_package"
    mock_dependencies["mock_pytest_main"].return_value = 1  # Simulate pytest failure
    mock_dependencies["mock_Coverage"].return_value.load.side_effect = NoDataError
    assert _run_unit_tests(compare_coverage=False, with_configs=False) is False


def test_run_unit_tests_function_success(mocker, mock_dependencies):
    mocker.patch("sys.exit")
    mock_dependencies["mock_pytest_main"].return_value = 0  # Simulate pytest success
    run_unit_tests(with_configs=False)
    sys.exit.assert_called_once_with(0)


def test_run_unit_tests_function_failure(mocker, mock_dependencies):
    mocker.patch("sys.exit")
    mock_dependencies["mock_pytest_main"].return_value = 1  # Simulate pytest failure
    run_unit_tests(with_configs=False)
    sys.exit.assert_called_once_with(1)


def test_run_unit_tests_with_coverage_function_success(mocker, mock_dependencies):
    mocker.patch("sys.exit")
    mock_dependencies["mock_pytest_main"].return_value = 0  # Simulate pytest success
    run_unit_tests_with_coverage(with_configs=False)
    sys.exit.assert_called_once_with(0)


def test_run_unit_tests_with_coverage_function_failure(mocker, mock_dependencies):
    mocker.patch("sys.exit")
    mock_dependencies["mock_pytest_main"].return_value = 1  # Simulate pytest failure
    run_unit_tests_with_coverage(with_configs=False)
    sys.exit.assert_called_once_with(1)
