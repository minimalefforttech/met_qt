# met_qt
Python based Qt Utilities and components

## Overview

Met Qt provides utilities and components to simplify Qt application development in Python. It supports both PySide2 (Qt5) and PySide6 (Qt6).

## Features

## Status

This project is under active development and prior to v1.0 may include breaking changes.
See the decision records in `docs/decision-records/` for design details and rationale.
If you incorporate any of these tools in your pipeline ensure that you set an appropriate minor version limit.
Patch versions may be assumed to be api compatible.

Currently this has only been tested in windows, but should work on other systems.

## License

MIT License - See LICENSE file for details.


## Installation

```bash
pip install git+https://github.com/minimalefforttech/met_qt.git
```

## Development

### Running Tests

The project includes tests for both PySide2 and PySide6. Use the provided test script:

```bash
# Run all tests
.\run_all_tests.bat

# Run specific version
.\run_all_tests.bat --pyside2  # For PySide2 only
.\run_all_tests.bat --pyside6  # For PySide6 only

# Force clean environment
.\run_all_tests.bat --clean
```
