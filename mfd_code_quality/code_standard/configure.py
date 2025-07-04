# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""
Configure coding standard files.

What script does:
- copy .pre-commit-config.yaml
- create pyproject.toml basing on generic configuration from generic_pyproject.toml and custom pyproject.toml file in
target repository
- create ruff.toml basing on generic configuration from generic_ruff.toml and custom ruff.toml file in target
repository
- install pre-commit hooks.

Script is made to be run from repository's root directory because .pre-commit-config.yaml, pyproject.toml and ruff.toml
file must be placed there.
"""

import logging
import os
import pathlib
import re
import shutil
import subprocess
import sys
from codecs import open as codec_open

from jinja2 import Template

from mfd_code_quality.utils import set_up_logging, get_root_dir

logger = logging.getLogger(__name__)


class ToolConfig:
    """Class for .toml options."""

    def __init__(self, tool_name: str):
        """Initialize ToolConfig."""
        self.tool_name = tool_name
        self.tool_options: dict[str, str] = {}

    def __eq__(self, other: "ToolConfig"):
        return self.tool_name.strip() == other.tool_name.strip()


def get_module_list() -> list[str]:
    """
    Get list of modules with configs per module.

    Read "config_per_module" directory file and return list of modules.
    Files contains <module_name>_<config_name> format.
    List should contain unique module names.

    :return: List of modules with configs per module.
    """
    possible_config_suffix = ["_pyproject.toml", "_ruff.toml"]
    _config_per_module_list = []
    config_per_module_dir = pathlib.Path(os.path.abspath(os.path.dirname(__file__)), "config_per_module")
    for file in config_per_module_dir.iterdir():
        if file.is_file() and any(file.name.endswith(suffix) for suffix in possible_config_suffix):
            for suffix in possible_config_suffix:
                module_name = file.name.replace(suffix, "")
            if module_name not in _config_per_module_list:
                _config_per_module_list.append(module_name)
    return _config_per_module_list


config_per_module_list = get_module_list()


def _read_config_content(config_file_path: pathlib.Path) -> list[ToolConfig]:
    """
    Read config file content.

    :param config_file_path: .toml file path.
    :return: List of ToolConfig.
    """
    logger.info(f"Read content of config file: {config_file_path}")

    tool_config_list = []
    tool_config = None
    last_option = None

    option_pattern = r"(?P<option_name>.*)(?P<option_value>\s*=\s*.*\s*)"
    with codec_open(str(config_file_path), "r", "utf-8") as f:
        check_ruff_header = True
        for line in f:
            if (
                check_ruff_header
                and re.search(option_pattern, line)
                and (config_file_path.name.endswith("ruff.toml") or config_file_path.name == "generic_ruff.txt")
            ):
                # This is necessary to use current mechanism for substitution because ruff.toml config does not
                # have this section
                # Created ruff.toml file will not have this header
                tool_config = ToolConfig("[ruff]\n")
                tool_config_list.append(tool_config)
                check_ruff_header = False
            if line.startswith("#") or line.isspace():
                continue
            elif line.startswith("["):
                tool_config = ToolConfig(line)
                tool_config_list.append(tool_config)
                last_option = None
                check_ruff_header = False
            elif match := re.search(option_pattern, line):
                if tool_config is None:
                    continue
                tool_config.tool_options[match.group("option_name")] = match.group("option_value")
                last_option = match.group("option_name")
            else:
                if tool_config is not None and last_option is not None:
                    tool_config.tool_options[last_option] += line
    return tool_config_list


def configure_pre_commit() -> None:
    """Configure pre-commit hooks."""
    logger.info("Configure pre-commit hooks")

    pre_commit_version = subprocess.run(["pre-commit", "--version"], check=True, capture_output=True, text=True).stdout
    logger.info(f"pre-commit version: {pre_commit_version}")

    python_version = subprocess.run([sys.executable, "--version"], check=True, capture_output=True, text=True).stdout
    logger.info(f"python version: {python_version}")

    output = subprocess.run(["pre-commit", "install"], check=True, capture_output=True, text=True).stdout
    logger.info(output)


def _copy_common_files(script_path: pathlib.Path, destination_path: pathlib.Path) -> None:
    """
    Copy files to destined path.

    :param script_path: configure.py path in site-packages
    :param destination_path: root's directory in repository
    """
    common_files = [
        pathlib.Path(script_path, ".pre-commit-config.yaml"),
    ]

    for common_file in common_files:
        logger.info(f"Copy: {common_file}")
        dest = str(destination_path.joinpath(common_file.name))
        shutil.copy2(str(common_file), dest)
        if "pre-commit-config.yaml" in str(common_file):
            _substitute_pre_commit_hook_file(dest)


def _remove_common_files(destination_path: pathlib.Path) -> None:
    """
    Remove common files from destination path.

    :param destination_path: Repository's root directory.
    """
    common_files = [
        ".pre-commit-config.yaml",
    ]

    for common_file in common_files:
        file_path = destination_path.joinpath(common_file)
        if file_path.exists():
            logger.info(f"Remove: {file_path}")
            file_path.unlink()


def _get_mfd_module_name(destination_path: pathlib.Path) -> str:
    """
    Get MFD repository name.

    :param destination_path: Repository's root directory.
    :return: MFD repository name.
    :raises Exception: When MFD repository name couldn't be found.
    """
    root_directory_file_list = destination_path.iterdir()

    for directory in root_directory_file_list:
        if directory.is_dir():
            match = re.search(r"(?P<mfd_module_name>^((pytest_)*mfd_.*)|({{.*}}))", directory.name)
            if match:
                if "{{" in match.group("mfd_module_name"):  # cookiecutter template
                    return _get_template_repo_name(destination_path)
                return match.group("mfd_module_name")

    raise Exception("Script was not run in MFD repository!")


def _get_template_repo_name(destination_path: pathlib.Path) -> str:
    """
    Get template repository name from root .txt file.

    :param destination_path: Repository's root directory.
    :return: Template repository name.
    :raises Exception: When template repository name couldn't be found.
    """
    logger.debug("Looking for .txt with repository name.")
    repo_name_file = pathlib.Path(destination_path, "repo_name.txt")
    if repo_name_file.exists():
        repo_name = repo_name_file.read_text().strip()
        logger.debug(f"Repository name is: {repo_name}")
        return repo_name

    logger.debug(f"Repo name not found in {destination_path}")
    raise Exception("Script was not run in MFD repository!")


def _create_unified_tool_config_list(tool_config_lists: list[list[ToolConfig]]) -> list[ToolConfig]:
    """
    Create unified list with tool configs from generic and custom .toml files.

    :param tool_config_lists: List of lists that contains tool configs from custom and generic .toml file
    :return: Unified list with tool configs from generic and custom .toml files
    """
    unified_tool_config_list = []
    for tool_config_list in tool_config_lists:
        for tool_config in tool_config_list:
            if tool_config not in unified_tool_config_list:
                unified_tool_config_list.append(tool_config)
            else:
                index = unified_tool_config_list.index(tool_config)
                unified_tool_config_list[index] = tool_config

    return unified_tool_config_list


def _create_toml_file(unified_tool_config_list: list[ToolConfig], toml_file_path: str) -> None:
    """
    Create .toml file basing on unified tool configs from generic and custom .toml files.

    :param unified_tool_config_list: Unified list with tool configs from generic and custom .toml files
    :param toml_file_path: Generated .toml file path
    """
    logger.info(f"Create .toml file in path: {toml_file_path}")

    with codec_open(toml_file_path, "w", "utf-8") as f:
        first_section = True
        for tool_config in unified_tool_config_list:
            if not tool_config.tool_options:
                continue
            # ruff.toml forbids to use section [ruff] in config, and we were using it just for the sake of substitution
            if not tool_config.tool_name == "[ruff]\n":
                if not first_section:
                    f.write("\n")  # Add a new line before section header except for the first section
                f.write(tool_config.tool_name)
                first_section = False
            for option_name, option_value in tool_config.tool_options.items():
                f.write(option_name)
                if "\n" not in option_value:
                    f.write(f"{option_value}\n")
                else:
                    f.write(option_value)


def _remove_toml_file(toml_file_path: str) -> None:
    """
    Remove .toml file.

    :param toml_file_path: .toml file path
    """
    logger.info(f"Remove .toml file in path: {toml_file_path}")
    if os.path.exists(toml_file_path):
        os.remove(toml_file_path)


def _substitute_toml_file(toml_file_path: str) -> None:
    """
    Substitute .toml file with repos specific fields.

    :param toml_file_path: Generated .toml file path
    """
    logger.info(f"Substitute .toml file in path: {toml_file_path}")

    with codec_open(toml_file_path, "rt") as f:
        template = Template(f.read())

    toml_path = pathlib.Path(toml_file_path)
    mfd_module_name = _get_mfd_module_name(toml_path.parent)

    if "_template" in mfd_module_name:
        logger.info("Template repository, Cookiecutter found in module name, skipping substitution")
        return

    substitutions = {"mfd_module_name": mfd_module_name}
    rendered_template = template.render(substitutions)

    with codec_open(toml_file_path, "wt") as f:
        f.writelines(rendered_template)


def _substitute_pre_commit_hook_file(yaml_file_path: pathlib.Path | str) -> None:
    """
    Substitute .toml file with repos specific fields.

    :param yaml_file_path: Generated .toml file path
    """
    logger.info(f"Substitute .yaml file in path: {yaml_file_path}")

    with codec_open(yaml_file_path, "rt") as f:
        template = Template(f.read())

    from importlib.metadata import version as pkg_version

    mfd_code_quality_version = pkg_version("mfd_code_quality")

    substitutions = {"version": mfd_code_quality_version}
    rendered_template = template.render(substitutions)

    with codec_open(yaml_file_path, "wt") as f:
        f.writelines(rendered_template)


def create_toml_files(cwd: pathlib.Path, pwd: pathlib.Path, custom_config_name: str, generic_config_name: str) -> None:
    """
    Create .toml file using generic and custom configs.

    :param cwd: Current work directory
    :param pwd: Configure.py directory
    :param custom_config_name: Custom config name
    :param generic_config_name: Generic config name
    """
    config_lists = []
    custom_config_path = None
    module_name = _get_mfd_module_name(cwd)
    repo_config_path = pathlib.Path(cwd, custom_config_name)
    if repo_config_path.is_file():
        logger.info(f"Repo {custom_config_name} file exists.")
        repo_tool_config_list = _read_config_content(repo_config_path)
        config_lists.append(repo_tool_config_list)

    if module_name in config_per_module_list:
        custom_config_path = pathlib.Path(pwd, "config_per_module", f"{module_name}_{custom_config_name}")
        logger.info(f"Custom {custom_config_name} path: {custom_config_path}")

    generic_config_path = pathlib.Path(pwd, generic_config_name)
    logger.info(f"Generic {generic_config_name} path: {generic_config_path}")

    generic_tool_config_list = _read_config_content(generic_config_path)
    config_lists.append(generic_tool_config_list)
    if custom_config_path and custom_config_path.is_file():
        logger.info(f"Custom {custom_config_name} file exists.")
        custom_ruff_config_list = _read_config_content(custom_config_path)
        config_lists.append(custom_ruff_config_list)

    unified_config_list = _create_unified_tool_config_list(config_lists)
    toml_file_path = os.path.join(cwd, custom_config_name)
    _create_toml_file(unified_config_list, toml_file_path)

    _substitute_toml_file(toml_file_path)


def configure_code_standard() -> None:
    """Configure repository for coding standard checks."""
    set_up_logging()
    cwd = get_root_dir()
    pwd = pathlib.Path(os.path.abspath(os.path.dirname(__file__)))

    logger.info("Step 1/4 - Copy common files.")
    _copy_common_files(pwd, cwd)

    logger.info("Step 2/4 - Create pyproject.toml file.")
    create_toml_files(cwd, pwd, "pyproject.toml", "generic_pyproject.txt")

    logger.info("Step 3/4 - Create ruff.toml file.")
    create_toml_files(cwd, pwd, "ruff.toml", "generic_ruff.txt")

    logger.info("Step 4/4 - Configure pre commit hooks..")
    configure_pre_commit()


def create_config_files() -> None:
    """Create config files pyproject.toml and ruff.toml."""
    set_up_logging()
    cwd = get_root_dir()
    pwd = pathlib.Path(os.path.abspath(os.path.dirname(__file__)))

    logger.info("Step 1/2 - Create pyproject.toml file.")
    create_toml_files(cwd, pwd, "pyproject.toml", "generic_pyproject.txt")

    logger.info("Step 2/2 - Create ruff.toml file.")
    create_toml_files(cwd, pwd, "ruff.toml", "generic_ruff.txt")


def delete_config_files() -> None:
    """Delete config files pyproject.toml and ruff.toml."""
    set_up_logging()
    cwd = get_root_dir()
    pwd = pathlib.Path(os.path.abspath(os.path.dirname(__file__)))

    logger.info("Step 1/2 - Remove pyproject.toml")
    cleanup_toml_file(cwd, pwd, "pyproject.toml", "generic_pyproject.txt")

    logger.info("Step 2/2 - Remove ruff.toml")
    _remove_toml_file(os.path.join(cwd, "ruff.toml"))


def cleanup_toml_file(cwd: pathlib.Path, pwd: pathlib.Path, custom_config_name: str, generic_config_name: str) -> None:
    """
    Cleanup toml file.

    Remove dynamically added sections from toml file.

    Read generic config content and remove it from the custom toml file.
    """
    toml_path = pathlib.Path(cwd, custom_config_name)
    generic_config_path = pathlib.Path(pwd, generic_config_name)

    if not toml_path.exists() or not generic_config_path.exists():
        logger.debug(f"Cleanup skipped because {custom_config_name} or {generic_config_name} file does not exist.")
        return

    with codec_open(generic_config_path, "r", "utf-8") as f:
        generic_content = f.read()

    with codec_open(toml_path, "r", "utf-8") as f:
        toml_content = f.read()
    if toml_content == "" or generic_content == "":
        logger.debug(f"Cleanup skipped because {custom_config_name} or {generic_config_name} file is empty.")
        return

    generic_content_first_line = generic_content.splitlines()[0]
    toml_content = toml_content.split(generic_content_first_line, 1)[0].rstrip("\r\n")
    with codec_open(toml_path, "w", "utf-8") as f:
        f.write(toml_content)
