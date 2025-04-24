# met_qt
Python based Qt Utilities and components

## Overview

Met Qt provides utilities and components to simplify Qt application development in Python. It supports both PySide2 (Qt5) and PySide6 (Qt6).

## Features

### Property Bindings

Easily bind Qt properties between widgets with support for one-way, two-way, and expression bindings:

```python
from met_qt.core.binding import Bindings

# Setup widgets
spinbox = QSpinBox()
label = QLabel()
bindings = Bindings()

# Bind spinbox value to label text
bindings.bind(spinbox, "value").to(label, "text", str)

# Two-way binding between line edits
with bindings.bind_group() as group:
    group.add(edit1, "text")
    group.add(edit2, "text")

# Expression binding for full name
with bindings.bind_expression(full_name, "text", "{first} {last}") as expr:
    expr.bind("first", first_name, "text")
    expr.bind("last", last_name, "text")
```

### Paint Layout System

A flexible layout system for custom paint-based widgets (documentation coming soon).

## Installation

```bash
pip install met_qt
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

## Status

This project is under active development and prior to v1.0 may include breaking changes.
See the decision records in `docs/decision-records/` for design details and rationale.

## License

MIT License - See LICENSE file for details.
