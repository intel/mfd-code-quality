> [!IMPORTANT]  
> This project is under development. All source code and features on the main branch are for the purpose of testing or evaluation and not production ready.

# MFD Code Quality

This module provides a set of methods for checking code quality.\
**Along with the module installation, additional CLI tools appear in your environment.**

## Usage

![](docs/code_quality_demo.gif)

When installing `mfd-code-quality` package all the commands from table below will become available from command-line.\
So you can just type i.e. `mfd-help` in your terminal without a need to call it from Python.\
If command requires configuration, the config file will be automatically created and removed after execution.

### Available commands

| Command                        | Description                                                                                   |
|--------------------------------|-----------------------------------------------------------------------------------------------|
| `mfd-help`                     | Log available commands.                                                                       |
| `mfd-code-standard`            | Check code standard using Ruff (`format`, `check`) or flake8. Depending on what is available. |
| `mfd-code-format`              | Format code using `ruff check --fix` and `ruff format`.                                       |
| `mfd-import-tests`             | Try to import each Python file to check import problems.                                      |
| `mfd-system-tests`             | Run system tests.                                                                             |
| `mfd-unit-tests`               | Run unit tests.                                                                               |
| `mfd-unit-tests-with-coverage` | Run unittests and check if diff coverage (new code coverage) is reaching the threshold (**80%**). |
| `mfd-all-checks`               | Run all available checks.                                                                     |

### Available arguments (for all commands)

* `-p` / `--project-dir` - path to the root directory (default: current working directory)

* `-v` / `--verbose` - enable verbose output

> [!NOTE]
> All commands are expected to be run from the root directory of the project.\
> Recommended file structure:
> ```
> <project>
> ├── <package>
> │   ├── __init__.py
> │   ├── ...
> ├── tests
> │   ├── system
> │   │   ├── __init__.py
> │   │   └── ...
> │   ├── unit
> │   │   ├── __init__.py
> │   │   └── ...
> │   └── __init__.py
> ├── pyproject.toml
> ├── README.md
> └── ...
> ```

### Configuration files

We are using 2 configuration files (created/modified/removed automatically):

* `ruff.toml` - for ruff configuration

* `pyproject.toml` - for project/generic configuration

### Custom configuration

Some modules have custom configuration files. Files are stored in `mfd_code_quality/code_standard/config_per_module` directory. Configuration files are merged with generic one during configuration process.

## OS supported:

OS agnostic

## Issue reporting

If you encounter any bugs or have suggestions for improvements, you're welcome to contribute directly or open an issue [here](https://github.com/intel/mfd-code-quality/issues).
