"""
Pytest configuration file for met_qt tests.

This file contains configuration and common fixtures for pytest.
"""

import os
import sys
import pytest

# Add the python directory to the path so that modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "python")))

# Skip tests that require Qt if no Qt bindings are available
def pytest_configure(config):
    """Configure pytest."""
    try:
        from met_qt._internal import qtcompat
        # Mark which binding is being used
        if qtcompat.QT_BINDING == 'PySide6':
            config.addinivalue_line("markers", "pyside6: mark test as requiring PySide6")
        elif qtcompat.QT_BINDING == 'PySide2':
            config.addinivalue_line("markers", "pyside2: mark test as requiring PySide2")
    except ImportError:
        # No Qt bindings available, add a skip marker
        config.addinivalue_line("markers", "qt: mark test as requiring Qt bindings")

def pytest_collection_modifyitems(config, items):
    """Skip tests marked as requiring specific Qt versions if those bindings aren't available."""
    try:
        from met_qt._internal import qtcompat
        qt_binding = qtcompat.QT_BINDING
    except ImportError:
        # If no Qt bindings are available, skip all tests marked with qt
        skip_qt = pytest.mark.skip(reason="No Qt bindings available")
        for item in items:
            if "qt" in item.keywords:
                item.add_marker(skip_qt)
        return
    
    # Skip PySide6-specific tests if PySide2 is being used
    if qt_binding == 'PySide2':
        skip_pyside6 = pytest.mark.skip(reason="Test requires PySide6, but PySide2 is being used")
        for item in items:
            if "pyside6" in item.keywords:
                item.add_marker(skip_pyside6)
    
    # Skip PySide2-specific tests if PySide6 is being used
    elif qt_binding == 'PySide6':
        skip_pyside2 = pytest.mark.skip(reason="Test requires PySide2, but PySide6 is being used")
        for item in items:
            if "pyside2" in item.keywords:
                item.add_marker(skip_pyside2)