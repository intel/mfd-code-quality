# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Tests for utils.py."""

import logging

from unittest.mock import patch, MagicMock
from mfd_code_quality.utils import (
    CustomFilter,
    set_up_basic_config,
    set_up_logging,
    get_parsed_args,
    get_root_dir,
    set_cwd,
    _install_packages,
)
from argparse import Namespace
from pathlib import Path


def test_check_if_log_message_is_from_module(mocker):
    mocker.patch("mfd_code_quality.utils.logging.Filter.filter", return_value=True)
    custom_filter = CustomFilter()
    record = MagicMock()
    record.name = "mfd_code_quality.utils"
    assert custom_filter.filter(record)


def test_set_up_basic_logging_config(mocker):
    mock_basic_config = mocker.patch("mfd_code_quality.utils.logging.basicConfig")
    set_up_basic_config(logging.DEBUG)
    mock_basic_config.assert_called_with(
        level=logging.DEBUG, format="%(asctime)s | %(name)35.35s | %(levelname)5.5s | %(msg)s"
    )


def test_set_up_logging_to_print_only_logs_from_this_file(mocker):
    mock_set_up_basic_config = mocker.patch("mfd_code_quality.utils.set_up_basic_config")
    mock_get_logger = mocker.patch("mfd_code_quality.utils.logging.getLogger")
    mock_handler = MagicMock()
    mock_get_logger.return_value.handlers = [mock_handler]
    set_up_logging()
    mock_set_up_basic_config.assert_called_once_with(log_level=logging.DEBUG)


def test_get_parsed_command_line_arguments(mocker):
    mock_parse_args = mocker.patch("mfd_code_quality.utils.ArgumentParser.parse_args")
    mock_parse_args.return_value = Namespace(project_dir="/path/to/project")
    args = get_parsed_args()
    assert args.project_dir == "/path/to/project"


@patch("mfd_code_quality.utils.get_parsed_args")
@patch("mfd_code_quality.utils.os.getcwd")
def test_get_root_directory(mock_getcwd, mock_get_parsed_args):
    mock_get_parsed_args.return_value = Namespace(project_dir=None)
    mock_getcwd.return_value = "/current/working/directory"
    root_dir = get_root_dir()
    assert root_dir == Path("/current/working/directory")


def test_set_current_working_directory_and_add_it_to_path(mocker):
    mock_get_root_dir = mocker.patch("mfd_code_quality.utils.get_root_dir")
    mock_chdir = mocker.patch("mfd_code_quality.utils.os.chdir")
    mock_sys_path = mocker.patch("mfd_code_quality.utils.sys.path", new_callable=list)
    mock_get_root_dir.return_value = Path("/new/working/directory")
    set_cwd()
    mock_chdir.assert_called_once_with(Path("/new/working/directory"))
    assert str(Path("/new/working/directory")) in mock_sys_path


def test_install_packages_from_list(mocker):
    mock_pip_main = mocker.patch("mfd_code_quality.utils.run")
    sys_mock = mocker.patch("mfd_code_quality.utils.sys")
    sys_mock.executable = "python"

    path_to_reqs = "path/to/reqs"
    _install_packages(path_to_reqs)

    mock_pip_main.assert_called_once_with(
        ("python", "-m", "pip", "install", "-r", "path/to/reqs"), capture_output=True, text=True
    )
