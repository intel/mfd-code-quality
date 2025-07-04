# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
from textwrap import dedent

import logging
import pytest

from mfd_code_quality.code_standard.checks import _get_available_code_standard_module, _test_ruff_check, run_checks


class TestChecks:
    def test_get_available_code_standard_module_flake8(self, mocker):
        output = dedent(
            """\
            flake8                  7.1.1
            flake8-annotations      3.0.1
            flake8-black            0.2.4
            """
        )
        mocker.patch("mfd_code_quality.code_standard.checks.run", return_value=mocker.Mock(stdout=output))
        mocker.patch("mfd_code_quality.code_standard.checks.get_root_dir", return_value="/path/to/root")
        assert _get_available_code_standard_module() == "flake8"

    def test_get_available_code_standard_module_ruff(self, mocker):
        output = dedent(
            """\
            ruff                    0.6.4
            flake8-annotations      3.0.1
            flake8-black            0.2.4
            """
        )
        mocker.patch("mfd_code_quality.code_standard.checks.run", return_value=mocker.Mock(stdout=output))
        mocker.patch("mfd_code_quality.code_standard.checks.get_root_dir", return_value="/path/to/root")
        assert _get_available_code_standard_module() == "ruff"

    def test_get_available_code_standard_module_none(self, mocker):
        mocker.patch("mfd_code_quality.code_standard.checks.run", return_value=mocker.Mock(stdout=""))
        mocker.patch("mfd_code_quality.code_standard.checks.get_root_dir", return_value="/path/to/root")
        with pytest.raises(Exception) as excinfo:
            _get_available_code_standard_module()
        assert "No code standard module is available! [flake8 or ruff]" in str(excinfo.value)

    def test__test_ruff_check_call(self, mocker, caplog):
        caplog.set_level(logging.INFO)
        mocker.patch("mfd_code_quality.code_standard.checks.run", return_value=mocker.Mock(returncode=1))
        mocker.patch("mfd_code_quality.code_standard.checks.get_root_dir", return_value="/path/to/root")
        _test_ruff_check()
        assert "Checking 'ruff check'..." in caplog.text

    def test_run_checks_failure(self, mocker, caplog):
        output = dedent(
            """\
            ruff                   0.6.4
            """
        )
        mocker.patch("mfd_code_quality.code_standard.checks.run", return_value=mocker.Mock(stdout=output))
        mocker.patch("mfd_code_quality.code_standard.checks.get_root_dir", return_value="/path/to/root")
        mocker.patch("mfd_code_quality.code_standard.checks.set_cwd")
        mocker.patch("mfd_code_quality.code_standard.checks.sys.exit", return_value=mocker.Mock())
        caplog.set_level(logging.INFO)
        run_checks(with_configs=False)
        assert "Code standard check FAILED." in caplog.text

    def test_run_checks_with_configs(self, mocker):
        mocker.patch("mfd_code_quality.code_standard.checks.sys.exit", return_value=mocker.Mock())
        create_mock = mocker.patch("mfd_code_quality.code_standard.checks.create_config_files")
        delete_mock = mocker.patch("mfd_code_quality.code_standard.checks.delete_config_files")
        mocker.patch("mfd_code_quality.code_standard.checks.set_cwd")
        mocker.patch(
            "mfd_code_quality.code_standard.checks._get_available_code_standard_module",
            return_value="ruff",
        )
        mocker.patch("mfd_code_quality.code_standard.checks._test_ruff_format", return_value=True)
        mocker.patch("mfd_code_quality.code_standard.checks._test_ruff_check", return_value=True)
        run_checks()
        create_mock.assert_called_once()
        delete_mock.assert_called_once()
