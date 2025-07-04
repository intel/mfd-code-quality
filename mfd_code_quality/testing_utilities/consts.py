# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Testing related consts."""

import pytest

PYTEST_OK_STATUSES = [pytest.ExitCode.OK, pytest.ExitCode.NO_TESTS_COLLECTED]

BERTA_IMPORTS = {
    "wrappers",
    "utils",
    "consts",
    "reslog",
    "repository",
    "py2py3",
    "wrappers.buildinstallers",
    "wrappers.drv_nicinstaller",
    "wrappers.nvm_nicupdater",
}
