# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Test testing_utilities.import_tests."""

import pytest
from unittest import mock


@pytest.fixture()
def mock_import_module():
    with mock.patch("mfd_code_quality.testing_utilities.import_tests.import_module") as mock_func:
        yield mock_func


@pytest.fixture
def mock_glob():
    with mock.patch("glob.iglob") as mock_func:
        yield mock_func


@pytest.fixture
def mock_get_parsed_args():
    with mock.patch("mfd_code_quality.utils.get_parsed_args") as mock_func:
        mock_func.return_value = mock.Mock(project_dir=None)
        yield mock_func


def test_run_import_tests_successful_import(mock_import_module, mock_glob, mocker):
    mocker.patch("mfd_code_quality.testing_utilities.import_tests.find_packages", return_value=["mfd-code-quality"])
    mocker.patch("mfd_code_quality.testing_utilities.import_tests.get_root_dir")
    mocker.patch("mfd_code_quality.testing_utilities.import_tests.set_up_logging")
    mocker.patch("mfd_code_quality.testing_utilities.import_tests.set_cwd")
    mocker.patch("mfd_code_quality.testing_utilities.import_tests.os.listdir", return_value=["aaa"])
    from mfd_code_quality.testing_utilities.import_tests import _run_import_tests

    mock_glob.return_value = ["mfd/module1.py", "mfd/module2.py"]
    mock_import_module.return_value = None
    assert _run_import_tests() is True


def test_run_import_tests_failed_import(mocker, mock_glob):
    mocker.patch("mfd_code_quality.testing_utilities.import_tests.set_up_logging")
    mocker.patch("mfd_code_quality.testing_utilities.import_tests.set_cwd")
    mocker.patch("mfd_code_quality.testing_utilities.import_tests.get_root_dir")
    mocker.patch("mfd_code_quality.testing_utilities.import_tests.find_packages", return_value=["mfd"])
    mocker.patch("mfd_code_quality.testing_utilities.import_tests.os.listdir", return_value=["aaa"])
    from mfd_code_quality.testing_utilities.import_tests import _run_import_tests

    mock_glob.return_value = ["mfd/module1.py", "mfd/module2.py"]
    mock_import_module.side_effect = Exception("Import error")
    assert _run_import_tests() is False


def test_run_import_tests_failed_import_with_requirements_installation(mocker, mock_glob):
    mocker.patch("mfd_code_quality.testing_utilities.import_tests.set_up_logging")
    mocker.patch("mfd_code_quality.testing_utilities.import_tests.set_cwd")
    mocker.patch("mfd_code_quality.testing_utilities.import_tests.get_root_dir")
    mocker.patch("mfd_code_quality.testing_utilities.import_tests.find_packages", return_value=["mfd"])
    mocker.patch("mfd_code_quality.testing_utilities.import_tests.os.listdir", return_value=["aaa", "requirements.txt"])
    mocker.patch("mfd_code_quality.testing_utilities.import_tests._install_packages")
    mock_glob.return_value = ["mfd/module1.py", "mfd/module2.py"]
    from mfd_code_quality.testing_utilities.import_tests import _run_import_tests

    mock_import_module.side_effect = Exception("Import error")
    assert _run_import_tests() is False


def test_run_checks_exits_with_zero_on_success(mocker):
    mocker.patch("mfd_code_quality.testing_utilities.import_tests._run_import_tests", return_value=True)
    from mfd_code_quality.testing_utilities.import_tests import run_checks

    with mock.patch("sys.exit") as mock_exit:
        run_checks()
        mock_exit.assert_called_once_with(0)


def test_run_checks_exits_with_one_on_failure(mocker):
    mocker.patch("mfd_code_quality.testing_utilities.import_tests._run_import_tests", return_value=False)
    from mfd_code_quality.testing_utilities.import_tests import run_checks

    with mock.patch("sys.exit") as mock_exit:
        run_checks()
        mock_exit.assert_called_once_with(1)
