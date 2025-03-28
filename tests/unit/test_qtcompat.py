"""
Tests for the Qt compatibility layer.

These tests verify that the compatibility functions in qtcompat.py work correctly
across different Qt versions (PySide2/PySide6).
"""

import sys
import unittest
import pytest
from unittest import mock

# Import the module under test
sys.path.insert(0, "c:/projects/git/met_qt/python")
from met_qt._internal import qtcompat

@pytest.mark.parametrize('qt_binding', [qtcompat.QT_BINDING])
class TestQtCompat:
    """Test the Qt compatibility layer functions."""
    
    @pytest.fixture(autouse=True)
    def setup_qt_binding(self, qt_binding):
        """Setup the Qt binding for each test."""
        self.original_binding = qtcompat.QT_BINDING
        with mock.patch.object(qtcompat, 'QT_BINDING', qt_binding):
            yield
        qtcompat.QT_BINDING = self.original_binding
    
    def test_qt_binding_identification(self):
        """Test that the Qt binding is correctly identified."""
        assert qtcompat.QT_BINDING in ['PySide2', 'PySide6']
        assert qtcompat.QT_VERSION is not None
    
    def test_import_qt_module(self):
        """Test the import_qt_module function."""
        # Test importing a module that should exist
        widgets_module = qtcompat.import_qt_module("Widgets")
        assert widgets_module is not None
        
        # Test importing a module that likely doesn't exist
        with mock.patch('warnings.warn') as mock_warn:
            with mock.patch('importlib.import_module', side_effect=ImportError("Test import error")):
                nonexistent_module = qtcompat.import_qt_module("NonexistentModule")
                assert nonexistent_module is None
                mock_warn.assert_called_once()
    
    def test_create_application(self):
        """Test the create_application function."""
        # Mock QApplication to avoid creating a real one during tests
        with mock.patch(f'{qtcompat.QT_BINDING}.QtWidgets.QApplication') as mock_qapp:
            # Test with default args
            qtcompat.create_application()
            mock_qapp.assert_called_once()
            args = mock_qapp.call_args[0][0]
            assert args == sys.argv
            
            mock_qapp.reset_mock()
            
            # Test with custom args
            custom_args = ['test', '--arg1', '--arg2']
            qtcompat.create_application(custom_args)
            mock_qapp.assert_called_once()
            args = mock_qapp.call_args[0][0]
            assert args == custom_args
    
    def test_get_query_bound_values(self):
        """Test the get_query_bound_values function."""
        # Create a mock query object without boundValues
        mock_query_no_bound = mock.Mock(spec=[])
        result = qtcompat.get_query_bound_values(mock_query_no_bound)
        assert result == {}
        
        if qtcompat.QT_BINDING == 'PySide6':
            # Test PySide6-like query (returns dict)
            mock_query = mock.Mock()
            expected_dict = {'param1': 'value1', 'param2': 'value2'}
            mock_query.boundValues.return_value = expected_dict
            result = qtcompat.get_query_bound_values(mock_query)
            assert result == expected_dict
            
        else:
            # Test PySide2-like query (returns list)
            mock_query = mock.Mock()
            bound_list = ['value1', 'value2']
            expected_dict = {0: 'value1', 1: 'value2'}
            mock_query.boundValues.return_value = bound_list
            result = qtcompat.get_query_bound_values(mock_query)
            assert result == expected_dict
    
    def test_get_touch_points(self):
        """Test the get_touch_points function."""
        if qtcompat.QT_BINDING == 'PySide6':
            # Test PySide6 behavior (uses points method)
            mock_touch_event = mock.Mock()
            touch_points = [mock.Mock(), mock.Mock()]
            mock_touch_event.points.return_value = touch_points
            result = qtcompat.get_touch_points(mock_touch_event)
            mock_touch_event.points.assert_called_once()
            assert result == touch_points
            
        else:
            # Test PySide2 behavior (uses touchPoints method)
            mock_touch_event = mock.Mock()
            touch_points = [mock.Mock(), mock.Mock()]
            mock_touch_event.touchPoints.return_value = touch_points
            result = qtcompat.get_touch_points(mock_touch_event)
            mock_touch_event.touchPoints.assert_called_once()
            assert result == touch_points
