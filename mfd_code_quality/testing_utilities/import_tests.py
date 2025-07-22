# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Import tests utilities."""

import glob
import logging
import os
import re
import sys
import traceback
from importlib import import_module

from setuptools import find_packages

from ..utils import _install_packages, get_root_dir, set_cwd, set_up_logging
from .consts import BERTA_IMPORTS

logger = logging.getLogger("mfd-code-quality.import_tests")


def _run_import_tests() -> bool:
    """
    Detect packages in the project, install their requirements and import all python files in the project.

    This is done to check if all files can be imported and will not crash due to incorrect import or similar issues.
    :return: True if all files can be imported successfully, False otherwise.
    """
    set_up_logging()
    set_cwd()
    successfully_imported = True
    root_dir = get_root_dir()
    packages = find_packages(where=root_dir, exclude=["tests", "tests.*"])
    paths = [os.path.join(root_dir, package.replace(".", "/")) for package in packages]

    for path, package in zip(paths, packages):
        if "requirements.txt" in os.listdir(path):
            logger.debug(f"'requirements.txt' found in: {path}")
            path_to_req = os.path.join(path, "requirements.txt")
            logger.debug(f"Installing requirements from {path_to_req}")
            _install_packages(path_to_req)

        for py_file in glob.iglob("*.py", root_dir=path, recursive=False):
            name = re.sub(r"[\\/]+", ".", py_file).removesuffix(".py")
            if "__main__" in name:  # skip https://docs.python.org/3/library/__main__.html
                continue
            try:
                name = package + "." + name
                import_module(name)
            except Exception as e:
                if isinstance(e, ModuleNotFoundError) and "berta_wrappers" in name:
                    if e.name in BERTA_IMPORTS:
                        logger.debug(f"Found import of berta module in {name}, skipping... Details: {e}")
                        continue

                logger.error("".join(traceback.format_exception(e)))
                successfully_imported = False

    if successfully_imported:
        logger.info("Import testing check PASSED.")

    return successfully_imported


def run_checks() -> None:
    """
    Execute each python file found in *mfd* folder and its sub-folders.

    This is done to check if all files can be imported and will not crash due to incorrect import or similar issues.
    """
    successfully_imported = _run_import_tests()
    sys.exit(0 if successfully_imported else 1)
