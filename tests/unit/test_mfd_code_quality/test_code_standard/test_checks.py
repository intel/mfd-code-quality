# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
from textwrap import dedent

import logging
import sys

import pytest

from mfd_code_quality.code_standard.checks import (
    _get_available_code_standard_module,
    _run_code_standard_tests,
    _test_ruff_check,
)


class TestChecks:
    def test_get_available_code_standard_module_flake8(self, mocker):
        """flake8 is chosen when ruff is not present but flake8 is."""
        # First command (uv pip list) returns no ruff / flake8
        mocker.patch(
            "mfd_code_quality.code_standard.checks.run",
            side_effect=[
                mocker.Mock(stdout="", returncode=0),
                mocker.Mock(
                    stdout=dedent(
                        """\
                        flake8                  7.1.1
                        flake8-annotations      3.0.1
                        flake8-black            0.2.4
                        """
                    ),
                    returncode=0,
                ),
            ],
        )
        mocker.patch("mfd_code_quality.code_standard.checks.get_root_dir", return_value="/path/to/root")

        assert _get_available_code_standard_module() == "flake8"

    def test_get_available_code_standard_module_ruff_preferred(self, mocker):
        """Ruff is preferred when both ruff and flake8 are installed."""
        output = dedent(
            """\
            ruff                    0.6.4
            flake8                  7.1.1
            flake8-annotations      3.0.1
            flake8-black            0.2.4
            """
        )
        mocker.patch(
            "mfd_code_quality.code_standard.checks.run",
            return_value=mocker.Mock(stdout=output, returncode=0),
        )
        mocker.patch("mfd_code_quality.code_standard.checks.get_root_dir", return_value="/path/to/root")

        assert _get_available_code_standard_module() == "ruff"

    def test_get_available_code_standard_module_none(self, mocker):
        mocker.patch(
            "mfd_code_quality.code_standard.checks.run",
            return_value=mocker.Mock(stdout="", returncode=0),
        )
        mocker.patch("mfd_code_quality.code_standard.checks.get_root_dir", return_value="/path/to/root")
        with pytest.raises(Exception) as excinfo:
            _get_available_code_standard_module()
        assert "No code standard module is available! [flake8 or ruff]" in str(excinfo.value)

    def test__test_ruff_check_call(self, mocker, caplog):
        caplog.set_level(logging.INFO)
        mocker.patch(
            "mfd_code_quality.code_standard.checks.run",
            return_value=mocker.Mock(returncode=1, stdout=""),
        )
        mocker.patch("mfd_code_quality.code_standard.checks.get_root_dir", return_value="/path/to/root")
        _test_ruff_check()
        assert "Checking 'ruff check'..." in caplog.text

    def test_run_code_standard_tests_failure_logs_and_returns_false(self, mocker, caplog):
        """When ruff checks fail, helper returns False and logs failure message."""
        caplog.set_level(logging.INFO)
        mocker.patch("mfd_code_quality.code_standard.checks.set_up_logging")
        mocker.patch("mfd_code_quality.code_standard.checks.set_cwd")
        mocker.patch(
            "mfd_code_quality.code_standard.checks._get_available_code_standard_module",
            return_value="ruff",
        )
        mocker.patch(
            "mfd_code_quality.code_standard.checks._test_ruff_format",
            return_value=False,
        )
        mocker.patch(
            "mfd_code_quality.code_standard.checks._test_ruff_check",
            return_value=False,
        )
        delete_mock = mocker.patch("mfd_code_quality.code_standard.checks.delete_config_files")
        create_mock = mocker.patch("mfd_code_quality.code_standard.checks.create_config_files")

        result = _run_code_standard_tests(with_configs=False)

        assert result is False
        assert "Code standard check FAILED." in caplog.text
        # with_configs=False -> no config files should be touched
        create_mock.assert_not_called()
        delete_mock.assert_not_called()

    def test_run_code_standard_tests_with_configs_calls_create_and_delete(self, mocker, caplog):
        """With configs enabled and ruff selected, config files are created and deleted in finally block."""
        caplog.set_level(logging.INFO)
        mocker.patch("mfd_code_quality.code_standard.checks.set_up_logging")
        mocker.patch("mfd_code_quality.code_standard.checks.set_cwd")
        mocker.patch(
            "mfd_code_quality.code_standard.checks._get_available_code_standard_module",
            return_value="ruff",
        )
        mocker.patch(
            "mfd_code_quality.code_standard.checks._test_ruff_format",
            return_value=True,
        )
        mocker.patch(
            "mfd_code_quality.code_standard.checks._test_ruff_check",
            return_value=True,
        )
        create_mock = mocker.patch("mfd_code_quality.code_standard.checks.create_config_files")
        delete_mock = mocker.patch("mfd_code_quality.code_standard.checks.delete_config_files")

        result = _run_code_standard_tests(with_configs=True)

        assert result is True
        create_mock.assert_called_once()
        delete_mock.assert_called_once()

    def test_run_checks_exits_with_correct_code(self, mocker):
        """High-level run_checks exits with 0/1 depending on helper result."""
        from mfd_code_quality.code_standard import checks

        mocker.patch.object(checks, "_run_code_standard_tests", return_value=True)
        exit_mock = mocker.patch.object(sys, "exit")

        checks.run_checks(with_configs=True)

        exit_mock.assert_called_once_with(0)

        # Now simulate failure
        exit_mock.reset_mock()
        mocker.patch.object(checks, "_run_code_standard_tests", return_value=False)

        checks.run_checks(with_configs=False)

        exit_mock.assert_called_once_with(1)

    def test_get_available_code_standard_module_uv_raises_then_fallback(self, mocker):
        """If the first command raises (e.g. uv missing), fallback command is used."""
        mocker.patch(
            "mfd_code_quality.code_standard.checks.run",
            side_effect=[
                FileNotFoundError(),  # simulates missing 'uv'
                mocker.Mock(
                    stdout=dedent(
                        """\
                        ruff                    0.6.4
                        flake8                  7.1.1
                        """
                    ),
                    returncode=0,
                ),
            ],
        )
        mocker.patch("mfd_code_quality.code_standard.checks.get_root_dir", return_value="/path/to/root")

        assert _get_available_code_standard_module() == "ruff"
