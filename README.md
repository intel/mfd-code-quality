> [!IMPORTANT]  
> This project is under development. All source code and features on the main branch are for the purpose of testing or evaluation and not production ready.

# MFD Code Quality

## Usage

This module provides set of code quality related methods with corresponding command line commands.

### Available commands

When installing `mfd-code-quality` package all these commands will become available from command line - in the same way as `pip` for example.\
So you can just type `mfd-help` in your terminal without a need to call it from Python.


> `mfd-configure-code-standard`\
> Prepare code standard configuration files into repository and setup pre commit.

> `mfd-create-config-files`\
> Prepare code standard configuration files into repository without setup of pre commit.\
> Mechanism of creating configs is the same as in 'mfd-configure-code-standard'.

> `mfd-code-standard`\
Run code standard test using ruff (format, check) or flake8. Depending on what is available. It copies configuration files before code standard check and remove their after check.
> It's not required to call `mfd-configure-code-standard` or `mfd-create-config-files` before running this command.

> `mfd-import-testing`\
Run import testing of each Python file to check import problems.

> `mfd-system-tests`\
Run system tests.

> `mfd-unit-tests`\
Run unittests, print actual coverage, but don't check its value.

> `mfd-unit-tests-with-coverage`\
Run unittests and check if diff coverage (new code coverage) is reaching the threshold.

> `mfd-all-checks`\
Run all available checks.

> `mfd-help`\
Log available commands.

> `mfd-format-code`\
Format code using ruff check --fix and ruff format

All commands can be combined with `--project-dir` parameter, which should point to the root directory of your repository.
If this parameter is not given current working directory will be assumed to be root directory.

### Configuration files
We are using 3 configuration files:
- `ruff.toml` - for ruff configuration
- `pyproject.toml` - for project/generic configuration
- `.pre-commit-config.yaml` - for pre-commit configuration

### Custom configuration
Some modules have custom configuration files. Files are stored in `mfd_code_quality/code_standard/config_per_module` directory. Configuration files are merged with generic one during configuration process.

## OS supported:

OS agnostic

## Issue reporting

If you encounter any bugs or have suggestions for improvements, you're welcome to contribute directly or open an issue [here](https://github.com/intel/mfd-code-quality/issues).
