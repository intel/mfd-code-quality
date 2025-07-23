# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
import pytest
from unittest.mock import patch, MagicMock
import sys

from mfd_code_quality.code_standard.formats import (
    _run_linter,
    _run_formatter,
    format_code,
)


class TestCodeStandard:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, mocker):
        # Setup: Mocking get_root_dir and run
        with (
            patch(
                "mfd_code_quality.code_standard.formats.get_root_dir",
                return_value="/mocked/path",
            ),
            patch("mfd_code_quality.code_standard.formats.run") as mock_run,
        ):
            mocker.patch("mfd_code_quality.code_standard.formats.create_config_files")
            mocker.patch("mfd_code_quality.code_standard.formats.delete_config_files")
            yield mock_run
            # Teardown: No specific teardown needed

    def test_run_linter_success(self, setup_and_teardown):
        mock_run = setup_and_teardown
        mock_run.return_value = MagicMock(returncode=0)
        assert _run_linter() is True
        mock_run.assert_called_once_with(
            (sys.executable, "-m", "ruff", "check", "--fix"), capture_output=True, text=True, cwd="/mocked/path"
        )

    def test_run_linter_failure(self, setup_and_teardown):
        mock_run = setup_and_teardown
        mock_run.return_value = MagicMock(returncode=1)
        assert _run_linter() is False
        mock_run.assert_called_once_with(
            (sys.executable, "-m", "ruff", "check", "--fix"), capture_output=True, text=True, cwd="/mocked/path"
        )

    def test_run_formatter_success(self, setup_and_teardown):
        mock_run = setup_and_teardown
        mock_run.return_value = MagicMock(returncode=0)
        assert _run_formatter() is True
        mock_run.assert_called_once_with(
            (sys.executable, "-m", "ruff", "format"), capture_output=True, text=True, cwd="/mocked/path"
        )

    def test_run_formatter_failure(self, setup_and_teardown):
        mock_run = setup_and_teardown
        mock_run.return_value = MagicMock(returncode=1)
        assert _run_formatter() is False
        mock_run.assert_called_once_with(
            (sys.executable, "-m", "ruff", "format"), capture_output=True, text=True, cwd="/mocked/path"
        )

    def test_format_code_success(self, setup_and_teardown):
        mock_run = setup_and_teardown
        mock_run.return_value = MagicMock(returncode=0)
        with patch("sys.exit") as mock_exit:
            format_code()
            mock_exit.assert_called_once_with(0)

    def test_format_code_linter_failure(self, setup_and_teardown):
        mock_run = setup_and_teardown
        mock_run.side_effect = [MagicMock(returncode=1), MagicMock(returncode=0)]
        with patch("sys.exit", side_effect=SystemExit) as mock_exit:
            with pytest.raises(SystemExit):
                format_code()
                mock_exit.assert_called_once_with(1)

    def test_format_code_formatter_failure(self, setup_and_teardown):
        mock_run = setup_and_teardown
        mock_run.side_effect = [MagicMock(returncode=0), MagicMock(returncode=1)]
        with patch("sys.exit", side_effect=SystemExit) as mock_exit:
            with pytest.raises(SystemExit):
                format_code()
                mock_exit.assert_called_once_with(1)
