# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Test testing_utilities.system_tests."""

from unittest import mock

import pytest

from mfd_code_quality.testing_utilities.system_tests import run_checks


@pytest.fixture
def mock_run_system_tests():
    with mock.patch("mfd_code_quality.testing_utilities.system_tests._run_system_tests") as mock_func:
        yield mock_func


def test_run_checks_exits_with_zero_on_success(mock_run_system_tests):
    mock_run_system_tests.return_value = True
    with mock.patch("sys.exit") as mock_exit:
        run_checks()
        mock_exit.assert_called_once_with(0)


def test_run_checks_exits_with_one_on_failure(mock_run_system_tests):
    mock_run_system_tests.return_value = False
    with mock.patch("sys.exit") as mock_exit:
        run_checks()
        mock_exit.assert_called_once_with(1)
