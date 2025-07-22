# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
import logging
import pathlib
from unittest.mock import mock_open

import pytest

from mfd_code_quality.code_standard.configure import (
    _substitute_toml_file,
    _create_toml_file,
    ToolConfig,
    _create_unified_tool_config_list,
    _get_module_name,
    _read_config_content,
    create_toml_files,
    create_config_files,
    delete_config_files,
    _remove_toml_file,
    _get_template_repo_name,
)


class TestConfigure:
    @pytest.fixture
    def tool_configs(self):
        tool_config_1 = ToolConfig("tool_1")
        tool_config_1.tool_options = {"option1": "value1", "option2": "value2"}

        tool_config_2 = ToolConfig("tool_2")
        tool_config_2.tool_options = {"optionA": "valueA\n", "optionB": "valueB"}

        return [tool_config_1, tool_config_2]

    def test_create_pyproject_toml_file(self, tool_configs, mocker):
        # Mock the codec_open function and the logger
        mock_codec_open = mocker.patch("mfd_code_quality.code_standard.configure.codec_open", mock_open())

        # Path to the pyproject.toml file
        pyproject_toml_file_path = "path/to/pyproject.toml"

        # Call the function under test
        _create_toml_file(tool_configs, pyproject_toml_file_path)

        # Check if the file was opened in write mode with utf-8 encoding
        mock_codec_open.assert_called_once_with(pyproject_toml_file_path, "w", "utf-8")

        # Check if the correct content was written to the file
        expected_calls = [
            mocker.call().write("tool_1"),
            mocker.call().write("option1"),
            mocker.call().write("value1\n"),
            mocker.call().write("option2"),
            mocker.call().write("value2\n"),
            mocker.call().write("\n"),
            mocker.call().write("tool_2"),
            mocker.call().write("optionA"),
            mocker.call().write("valueA\n"),  # valueA already contains a newline
            mocker.call().write("optionB"),
            mocker.call().write("valueB\n"),
        ]
        mock_codec_open.assert_has_calls(expected_calls, any_order=False)

    def test_create_unified_tool_config_list(self, tool_configs):
        # Create another instance with the same name as tool_config_1 but with different options
        tool_config_1_modified = ToolConfig("tool_1")
        tool_config_1_modified.tool_options = {"option1": "new_value1", "option3": "value3"}

        # Create a list of ToolConfig instances that simulates a custom pyproject.toml file
        custom_tool_configs = [tool_config_1_modified]

        # Call the function under test with the fixture and the custom list
        unified_list = _create_unified_tool_config_list([tool_configs, custom_tool_configs])

        assert len(unified_list) == 2
        assert unified_list[0] == tool_config_1_modified
        assert unified_list[1] == tool_configs[1]
        assert unified_list[0].tool_options == {"option1": "new_value1", "option3": "value3"}

    @pytest.mark.parametrize(
        "module_name, expected",
        [
            ("mfd_example", "mfd_example"),
            ("pytest_mfd_example", "pytest_mfd_example"),
            ("{{cookiecutter.project_slug}}", "mfd_module_template"),
        ],
    )
    def test_get_module_name_success(self, mocker, module_name, expected):
        # Mock the directory listing
        mock_path = mocker.MagicMock(spec=pathlib.Path)
        mock_directory = mocker.MagicMock(spec=pathlib.Path)
        mock_directory.name = module_name
        mock_path.iterdir.return_value = [mock_directory]

        # Call the function and assert the result
        mocker.patch("mfd_code_quality.code_standard.configure._get_template_repo_name", return_value=expected)
        mocker.patch("mfd_code_quality.code_standard.configure.get_package_name", return_value=expected)
        result = _get_module_name(mock_path)
        assert result == expected

    def test__get_template_repo_name(self, mocker, caplog):
        caplog.set_level(logging.DEBUG)
        mock_path = mocker.MagicMock(spec=pathlib.Path)
        mock_repo_name_file = mocker.MagicMock(spec=pathlib.Path)
        mock_repo_name_file.exists.return_value = True
        mock_repo_name_file.read_text.return_value = "some_repo"
        mock_pathlib = mocker.patch("mfd_code_quality.code_standard.configure.pathlib")
        mock_pathlib.Path.return_value = mock_repo_name_file
        result = _get_template_repo_name(mock_path)
        assert result == "some_repo"
        assert "Repository name is: some_repo" in caplog.text

    def test_get_mfd_module_name_failure(self, mocker):
        # Mock the directory listing with no matching directories
        mock_path = mocker.MagicMock(spec=pathlib.Path)
        mock_path.iterdir.return_value = []

        # Call the function and assert that an exception is raised
        with pytest.raises(Exception):
            _get_module_name(mock_path)

    def test_get_mfd_module_name_no_match(self, mocker):
        # Mock the directory listing with directories that do not match the pattern
        mock_path = mocker.MagicMock(spec=pathlib.Path)
        mock_directory1 = mocker.MagicMock(spec=pathlib.Path)
        mock_directory1.name = "not_mfd_dir"
        mock_directory1.is_dir.return_value = True
        mock_directory2 = mocker.MagicMock(spec=pathlib.Path)
        mock_directory2.name = "another_dir"
        mock_directory2.is_dir.return_value = True
        mock_path.iterdir.return_value = [mock_directory1, mock_directory2]

        # Call the function and assert that an exception is raised
        with pytest.raises(Exception):
            _get_module_name(mock_path)

    def test_read_pyproject_content_success(self, mocker):
        # Sample content of pyproject.toml
        sample_content = (
            "[tool.black]\nline-length = 88\ntarget-version = ['py37']\n[tool.isort]\nprofile = 'black'\n".encode(
                "utf-8"
            )
        )

        mocker.patch("builtins.open", mocker.mock_open(read_data=sample_content))

        match_line_length = mocker.MagicMock()
        match_line_length.group.return_value = "line-length = 88"

        match_target_version = mocker.MagicMock()
        match_target_version.group.return_value = "target-version = ['py37']"

        result = _read_config_content(pathlib.Path("/fake/path/pyproject.toml"))

        expected_tool_black = ToolConfig("[tool.black]\n")
        expected_tool_black.tool_options["line-length"] = " = 88\n"
        expected_tool_black.tool_options["target-version"] = " = ['py37']\n"

        expected_tool_isort = ToolConfig("[tool.isort]\n")
        expected_tool_isort.tool_options["profile"] = " = 'black\n'"

        assert result == [expected_tool_black, expected_tool_isort]

    def test_read_pyproject_content_empty_file(self, mocker):
        # Mocking an empty pyproject.toml
        mocker.patch("builtins.open", mocker.mock_open(read_data="".encode("utf-8")))

        result = _read_config_content(pathlib.Path("/fake/path/pyproject.toml"))

        assert result == [], "Should return an empty list for an empty file"

    def test_read_pyproject_content_with_comments(self, mocker):
        # Sample content with comments
        sample_content = "# This is a comment\n[tool.black]\n# Another comment\nline-length = 88\n".encode("utf-8")

        mocker.patch("builtins.open", mocker.mock_open(read_data=sample_content))

        result = _read_config_content(pathlib.Path("/fake/path/pyproject.toml"))

        expected_tool_black = ToolConfig("[tool.black]\n")
        expected_tool_black.tool_options["line-length"] = " = 88\n"

        assert result == [expected_tool_black]

    def test_read_pyproject_content_multiline_option(self, mocker):
        # Sample content of pyproject.toml with a multiline option
        sample_content = [
            "[tool.black]\n",
            "line-length = 88\n",
            "include = '\n",
            "    # Regex of paths to include\n",
            "    (?i)src/\n",
            "    tests/\n",
            "'\n",
        ]

        read_data = "".join(sample_content)
        mocker.patch("builtins.open", mocker.mock_open(read_data=read_data.encode("utf-8")))

        # Mocking re.search to return appropriate match objects with string results
        def mock_search(pattern, text):
            if "line-length" in text:
                match = mocker.MagicMock()
                match.group.return_value = "line-length = 88"
                return match
            elif "include" in text:
                match = mocker.MagicMock()
                match.group.return_value = "include = '\n"
                return match
            return None

        mocker.patch("re.search", side_effect=mock_search)

        result = _read_config_content(pathlib.Path("/fake/path/pyproject.toml"))

        expected_tool_black = ToolConfig("[tool.black]\n")
        expected_tool_black.tool_options["line-length"] = " = 88\n"
        expected_tool_black.tool_options["include"] = "\n    # Regex of paths to include\n    (?i)src/\n    tests/\n"

        assert result == [expected_tool_black], "The multiline option should be correctly appended to the last option"

    def test_substitute_pyproject_toml_file(self, mocker):
        mocker.patch("mfd_code_quality.code_standard.configure.logger")

        # Mocking the file operations
        mock_open = mocker.patch(
            "mfd_code_quality.code_standard.configure.codec_open",
            mocker.mock_open(read_data='name = "$mfd_module_name"'),
        )

        # Mocking the Template class and its render method
        mock_template = mocker.MagicMock()
        mock_template.render.return_value = 'name = "mfd_example_module"'
        mocker.patch("mfd_code_quality.code_standard.configure.Template", return_value=mock_template)

        # Mocking _get_module_name to return a specific module name
        mocker.patch("mfd_code_quality.code_standard.configure._get_module_name", return_value="mfd_example_module")

        _substitute_toml_file("/fake/path/pyproject.toml")

        mock_open.assert_called_with("/fake/path/pyproject.toml", "wt")
        handle = mock_open()
        handle.writelines.assert_called_once_with('name = "mfd_example_module"')

    def test_substitute_pyproject_toml_file_template_repo(self, mocker):
        mocker.patch("mfd_code_quality.code_standard.configure.logger")

        # Mocking the file operations
        mocker.patch(
            "mfd_code_quality.code_standard.configure.codec_open",
            mocker.mock_open(read_data='name = "$mfd_module_name"'),
        )

        # Mocking the Template class and its render method
        mock_template = mocker.MagicMock()
        mock_template.render.return_value = 'name = "mfd_example_module"'
        mocker.patch("mfd_code_quality.code_standard.configure.Template", return_value=mock_template)

        # Mocking _get_module_name to return a specific module name
        mocker.patch(
            "mfd_code_quality.code_standard.configure._get_module_name",
            return_value="{{cookiecutter.project_slug}}",
        )

        _substitute_toml_file("/fake/path/pyproject.toml")

    def test_substitute_pyproject_toml_file_with_error(self, mocker):
        mocker.patch("mfd_code_quality.code_standard.configure.logger")

        # Simulating an error during file reading
        mocker.patch("mfd_code_quality.code_standard.configure.codec_open", side_effect=IOError("Failed to open file"))

        with pytest.raises(IOError) as exc_info:
            _substitute_toml_file("/fake/path/pyproject.toml")

        assert str(exc_info.value) == "Failed to open file", "Should raise an IOError if the file cannot be opened"

    def test_create_config_files(self, mocker):
        mocker.patch("mfd_code_quality.code_standard.configure.set_up_logging")
        mocker.patch("mfd_code_quality.code_standard.configure.get_root_dir", return_value="/fake/root/dir")
        mocker.patch("os.path.abspath", return_value="/fake/dir")
        mocker.patch("os.path.dirname", return_value="/fake/dir")
        mocker.patch("mfd_code_quality.code_standard.configure.logger")
        create_toml_files_mock = mocker.patch("mfd_code_quality.code_standard.configure.create_toml_files")

        create_config_files()

        assert create_toml_files_mock.call_count == 2

    @pytest.mark.parametrize("custom_pyproject_exists, call_number", [(True, 3), (False, 1)])
    def test_create_toml_files_with_unique_config(self, custom_pyproject_exists, call_number, mocker):
        mocker.patch("pathlib.Path.is_file", return_value=custom_pyproject_exists)

        _read_pyproject_content_mock = mocker.patch(
            "mfd_code_quality.code_standard.configure._read_config_content", return_value=[mocker.MagicMock()]
        )
        _create_unified_tool_config_list_mock = mocker.patch(
            "mfd_code_quality.code_standard.configure._create_unified_tool_config_list",
            return_value=mocker.MagicMock(),
        )
        _create_pyproject_toml_file_mock = mocker.patch("mfd_code_quality.code_standard.configure._create_toml_file")
        _substitute_pyproject_toml_file_mock = mocker.patch(
            "mfd_code_quality.code_standard.configure._substitute_toml_file"
        )
        _substitute_pyproject_toml_file_mock = mocker.patch(
            "mfd_code_quality.code_standard.configure._get_module_name",
            return_value="mfd_connect",
        )
        cwd = mocker.MagicMock(retrurn_value=pathlib.Path)
        pwd = mocker.MagicMock(retrurn_value=pathlib.Path)
        create_toml_files(cwd, pwd, "custom.toml", "generic.txt")

        assert _read_pyproject_content_mock.call_count == call_number
        _create_unified_tool_config_list_mock.assert_called_once()
        _create_pyproject_toml_file_mock.assert_called_once()
        _substitute_pyproject_toml_file_mock.assert_called_once()

    def test_delete_config_files_success(self, mocker):
        mocker.patch("mfd_code_quality.code_standard.configure.set_up_logging")
        mocker.patch(
            "mfd_code_quality.code_standard.configure.get_root_dir",
            return_value="/fake/root/dir",
        )
        mocker.patch("os.path.join", side_effect=lambda *args: "/".join(args))
        mock_remove_toml_file = mocker.patch("mfd_code_quality.code_standard.configure._remove_toml_file")

        delete_config_files()

        mock_remove_toml_file.assert_any_call("/fake/root/dir/ruff.toml")

    def test_delete_config_files_failure(self, mocker):
        mocker.patch("mfd_code_quality.code_standard.configure.set_up_logging")
        mocker.patch(
            "mfd_code_quality.code_standard.configure.get_root_dir",
            return_value="/fake/root/dir",
        )
        mocker.patch("os.path.join", side_effect=lambda *args: "/".join(args))
        mock_remove_toml_file = mocker.patch(
            "mfd_code_quality.code_standard.configure._remove_toml_file",
            side_effect=Exception("Failed to remove file"),
        )
        mock_logger = mocker.patch("mfd_code_quality.code_standard.configure.logger")

        with pytest.raises(Exception, match="Failed to remove file"):
            delete_config_files()

            mock_logger.info.assert_any_call("Step 1/2 - Remove pyproject.toml")
            mock_logger.info.assert_any_call("Step 2/2 - Remove ruff.toml")
            mock_remove_toml_file.assert_any_call("/fake/root/dir/pyproject.toml")
            mock_remove_toml_file.assert_any_call("/fake/root/dir/ruff.toml")

    def test_remove_toml_file_success(self, mocker):
        mocker.patch("os.path.exists", return_value=True)
        mock_remove = mocker.patch("os.remove")

        _remove_toml_file("/fake/path/pyproject.toml")

        mock_remove.assert_called_once_with("/fake/path/pyproject.toml")

    def test_remove_toml_file_not_exists(self, mocker):
        mocker.patch("os.path.exists", return_value=False)
        mock_remove = mocker.patch("os.remove")

        _remove_toml_file("/fake/path/pyproject.toml")

        mock_remove.assert_not_called()

    def test_cleanup_toml_file_removes_generic_content(self, mocker):
        # Setup paths
        mock_cwd = mocker.MagicMock(spec=pathlib.Path)
        mock_pwd = mocker.MagicMock(spec=pathlib.Path)
        custom_config_name = "pyproject.toml"
        generic_config_name = "generic_pyproject.txt"
        toml_path = mocker.MagicMock(spec=pathlib.Path)
        generic_config_path = mocker.MagicMock(spec=pathlib.Path)
        # Patch only the Path instantiations in the module under test
        mocker.patch(
            "mfd_code_quality.code_standard.configure.pathlib.Path", side_effect=[toml_path, generic_config_path]
        )
        toml_path.exists.return_value = True
        generic_config_path.exists.return_value = True
        # Mock file contents
        generic_content = "[tool.black]\nline-length = 88\n"
        toml_content = "# custom section\n[tool.black]\nline-length = 88\nmore custom\n"
        m = mocker.patch("mfd_code_quality.code_standard.configure.codec_open", mocker.mock_open())
        m().read.side_effect = [generic_content, toml_content]

        # Call function
        from mfd_code_quality.code_standard import configure

        configure.cleanup_toml_file(mock_cwd, mock_pwd, custom_config_name, generic_config_name)

        # Should write only up to the first line of generic content
        handle = m()
        expected_written = "# custom section"
        handle.write.assert_called_once_with(expected_written)

    def test_cleanup_toml_file_skips_if_files_missing(self, mocker):
        mock_cwd = mocker.MagicMock(spec=pathlib.Path)
        mock_pwd = mocker.MagicMock(spec=pathlib.Path)
        custom_config_name = "pyproject.toml"
        generic_config_name = "generic_pyproject.txt"
        toml_path = mocker.MagicMock(spec=pathlib.Path)
        generic_config_path = mocker.MagicMock(spec=pathlib.Path)
        mocker.patch(
            "mfd_code_quality.code_standard.configure.pathlib.Path", side_effect=[toml_path, generic_config_path]
        )
        toml_path.exists.return_value = False
        generic_config_path.exists.return_value = True
        mock_logger = mocker.patch("mfd_code_quality.code_standard.configure.logger")
        from mfd_code_quality.code_standard import configure

        configure.cleanup_toml_file(mock_cwd, mock_pwd, custom_config_name, generic_config_name)

        mock_logger.debug.assert_called()

    def test_cleanup_toml_file_no_generic_line_found(self, mocker):
        mock_cwd = mocker.MagicMock(spec=pathlib.Path)
        mock_pwd = mocker.MagicMock(spec=pathlib.Path)
        custom_config_name = "pyproject.toml"
        generic_config_name = "generic_pyproject.txt"
        toml_path = mocker.MagicMock(spec=pathlib.Path)
        generic_config_path = mocker.MagicMock(spec=pathlib.Path)
        mocker.patch(
            "mfd_code_quality.code_standard.configure.pathlib.Path", side_effect=[toml_path, generic_config_path]
        )
        toml_path.exists.return_value = True
        generic_config_path.exists.return_value = True
        generic_content = "[tool.black]\nline-length = 88\n"
        toml_content = "# custom section\nmore custom\n"
        m = mocker.patch("mfd_code_quality.code_standard.configure.codec_open", mocker.mock_open())
        m().read.side_effect = [generic_content, toml_content]
        from mfd_code_quality.code_standard import configure

        configure.cleanup_toml_file(mock_cwd, mock_pwd, custom_config_name, generic_config_name)

        handle = m()
        handle.write.assert_called_once_with(toml_content.split("[tool.black]", 1)[0].rstrip("\r\n"))

    def test_cleanup_toml_file_empty_files(self, mocker):
        import pathlib

        mock_cwd = mocker.MagicMock(spec=pathlib.Path)
        mock_pwd = mocker.MagicMock(spec=pathlib.Path)
        custom_config_name = "pyproject.toml"
        generic_config_name = "generic_pyproject.txt"
        toml_path = mocker.MagicMock(spec=pathlib.Path)
        generic_config_path = mocker.MagicMock(spec=pathlib.Path)
        toml_path.exists.return_value = True
        generic_config_path.exists.return_value = True
        generic_content = ""
        toml_content = ""
        m = mocker.patch("mfd_code_quality.code_standard.configure.codec_open", mocker.mock_open())
        m().read.side_effect = [generic_content, toml_content]
        from mfd_code_quality.code_standard import configure

        configure.cleanup_toml_file(mock_cwd, mock_pwd, custom_config_name, generic_config_name)

        handle = m()
        handle.write.assert_not_called()
