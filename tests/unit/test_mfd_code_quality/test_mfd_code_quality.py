# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Tests for `mfd_code_quality` package."""

from unittest.mock import patch

import pytest

from mfd_code_quality.mfd_code_quality import run_all_checks, log_help_info


@pytest.fixture
def mock_dependencies():
    with (
        patch("mfd_code_quality.code_standard.checks._get_available_code_standard_module") as mock_get_module,
        patch("mfd_code_quality.code_standard.configure.create_config_files") as mock_create_config,
        patch("mfd_code_quality.code_standard.configure.delete_config_files") as mock_delete_config,
        patch("mfd_code_quality.code_standard.checks._run_code_standard_tests") as mock_code_standard_check,
        patch("mfd_code_quality.testing_utilities.import_tests._run_import_tests") as mock_import_tests_check,
        patch("mfd_code_quality.testing_utilities.system_tests._run_system_tests") as mock_system_tests_check,
        patch("mfd_code_quality.testing_utilities.unit_tests._run_unit_tests") as mock_unit_tests_with_coverage_check,
    ):
        yield {
            "mock_get_module": mock_get_module,
            "mock_create_config": mock_create_config,
            "mock_delete_config": mock_delete_config,
            "mock_code_standard_check": mock_code_standard_check,
            "mock_import_tests_check": mock_import_tests_check,
            "mock_system_tests_check": mock_system_tests_check,
            "mock_unit_tests_with_coverage_check": mock_unit_tests_with_coverage_check,
        }


def test_run_all_checks_with_ruff(mock_dependencies):
    mock_dependencies["mock_get_module"].return_value = "ruff"
    mock_dependencies["mock_code_standard_check"].return_value = True
    mock_dependencies["mock_import_tests_check"].return_value = True
    mock_dependencies["mock_system_tests_check"].return_value = True
    mock_dependencies["mock_unit_tests_with_coverage_check"].return_value = True

    result = run_all_checks()

    assert result is True
    mock_dependencies["mock_create_config"].assert_called_once()
    mock_dependencies["mock_delete_config"].assert_called_once()
    mock_dependencies["mock_code_standard_check"].assert_called_once_with(with_configs=False)
    mock_dependencies["mock_import_tests_check"].assert_called_once()
    mock_dependencies["mock_system_tests_check"].assert_called_once()
    mock_dependencies["mock_unit_tests_with_coverage_check"].assert_called_once_with(
        compare_coverage=True, with_configs=False
    )


def test_run_all_checks_with_flake8(mock_dependencies):
    mock_dependencies["mock_get_module"].return_value = "flake8"
    mock_dependencies["mock_code_standard_check"].return_value = True
    mock_dependencies["mock_import_tests_check"].return_value = True
    mock_dependencies["mock_system_tests_check"].return_value = True
    mock_dependencies["mock_unit_tests_with_coverage_check"].return_value = True

    result = run_all_checks()

    assert result is True
    mock_dependencies["mock_create_config"].assert_not_called()
    mock_dependencies["mock_delete_config"].assert_not_called()
    mock_dependencies["mock_code_standard_check"].assert_called_once_with(with_configs=False)
    mock_dependencies["mock_import_tests_check"].assert_called_once()
    mock_dependencies["mock_system_tests_check"].assert_called_once()
    mock_dependencies["mock_unit_tests_with_coverage_check"].assert_called_once_with(
        compare_coverage=True, with_configs=False
    )


def test_log_help_info_logs_commands(caplog, mocker):
    """log_help_info should log available commands without parsing real CLI args."""
    caplog.set_level("INFO")
    # Prevent argparse in set_up_logging/get_parsed_args from seeing pytest/IDE args.
    mocker.patch("mfd_code_quality.utils.get_parsed_args", return_value=mocker.Mock(verbose=False))

    log_help_info()

    assert "Available commands:" in caplog.text
