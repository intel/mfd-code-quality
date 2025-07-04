# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
import pathlib
from subprocess import CompletedProcess

from mfd_code_quality.coverage.utils import is_diff_coverage_threshold_reached


class TestUtils:
    def test_is_diff_coverage_threshold_reached(self, mocker):
        mocker.patch("mfd_code_quality.coverage.utils.run", return_value=CompletedProcess(args="", returncode=0))
        mocker.patch("mfd_code_quality.coverage.utils.get_root_dir", return_value=mocker.create_autospec(pathlib.Path))
        assert is_diff_coverage_threshold_reached() is True
