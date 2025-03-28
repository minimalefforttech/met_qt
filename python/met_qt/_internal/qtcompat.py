"""
Qt Compatibility Layer for PySide2/PySide6.

This module provides a unified API for working with either PySide2 or PySide6.
It attempts to import PySide6 first, and falls back to PySide2 if PySide6 is not available.
This is strictly for internal use within the met_qt project.
"""

import importlib
import sys
import warnings
from typing import Dict, Any, Tuple, Optional, Union, List, Callable

# Track which Qt binding we're using
QT_BINDING = ''
QT_VERSION = ''

# Try to import PySide6 first, fall back to PySide2
try:
    # Import all the requested Qt modules
    from PySide6 import (
        QtConcurrent, QtCore, QtGui, QtNetwork, QtQml, QtQuick, QtSvg,
        QtTest, QtWidgets, QtXml
    )
    
    # Try to import optional modules that might not be available in all installations
    try:
        from PySide6 import QtDBus
    except ImportError:
        QtDBus = None
    
    try:
        from PySide6 import QtQuick3D
    except ImportError:
        QtQuick3D = None
    
    try:
        from PySide6 import QtQuickControls2
    except ImportError:
        QtQuickControls2 = None
    
    try:
        from PySide6 import QtQuickTest
    except ImportError:
        QtQuickTest = None
    
    try:
        from PySide6 import QtQuickWidgets
    except ImportError:
        QtQuickWidgets = None
    
    try:
        from PySide6 import QtStateMachine
    except ImportError:
        QtStateMachine = None
    
    try:
        from PySide6 import QtSvgWidgets
    except ImportError:
        QtSvgWidgets = None
    
    try:
        from PySide6 import QtPrintSupport
    except ImportError:
        QtPrintSupport = None
    
    # Import Shiboken
    try:
        import shiboken6 as Shiboken
    except ImportError:
        Shiboken = None

    # Core elements
    from PySide6.QtCore import Qt, Signal, Slot, Property
    QT_BINDING = 'PySide6'
    QT_VERSION = QtCore.__version__

    # In Qt 6, QAction moved from QtWidgets to QtGui
    from PySide6.QtGui import QAction
    
except ImportError:
    try:
        # Import all the requested Qt modules for PySide2
        from PySide2 import (
            QtConcurrent, QtCore, QtGui, QtNetwork, QtQml, QtQuick, QtSvg, 
            QtTest, QtWidgets, QtXml
        )
        
        # Try to import optional modules that might not be available in all installations
        try:
            from PySide2 import QtDBus
        except ImportError:
            QtDBus = None
        
        # PySide2 doesn't have QtQuick3D in most installations
        QtQuick3D = None
        
        try:
            from PySide2 import QtQuickControls2
        except ImportError:
            QtQuickControls2 = None
        
        try:
            from PySide2 import QtQuickTest
        except ImportError:
            QtQuickTest = None
        
        try:
            from PySide2 import QtQuickWidgets
        except ImportError:
            QtQuickWidgets = None
        
        # In PySide2, it might be called QtStateMachine or QtState
        try:
            from PySide2 import QtStateMachine
        except ImportError:
            try:
                from PySide2 import QtState as QtStateMachine
            except ImportError:
                QtStateMachine = None
        
        # In PySide2, SVG widgets are part of QtSvg
        QtSvgWidgets = QtSvg
        
        try:
            from PySide2 import QtPrintSupport
        except ImportError:
            QtPrintSupport = None
        
        # Import Shiboken
        try:
            import shiboken2 as Shiboken
        except ImportError:
            Shiboken = None

        # Core elements
        from PySide2.QtCore import Qt, Signal, Slot, Property
        QT_BINDING = 'PySide2'
        QT_VERSION = QtCore.__version__
        
        # In PySide2, some constants have different locations
        # Map Qt.AlignmentFlag to Qt.Alignment for compatibility
        if not hasattr(Qt, 'AlignmentFlag'):
            Qt.AlignmentFlag = Qt.Alignment
        
        if not hasattr(Qt, 'WindowType'):
            Qt.WindowType = Qt.WindowFlags
            
        # In Qt 5, QAction is in QtWidgets, not QtGui
        from PySide2.QtWidgets import QAction
        
    except ImportError:
        raise ImportError("Neither PySide6 nor PySide2 could be imported. "
                         "Please install one of these packages.")

# Simplified imports for common modules
def import_qt_module(module_name: str) -> Any:
    """
    Import a Qt module dynamically based on the current binding.
    
    Args:
        module_name: Name of the module without the Qt prefix (e.g., "WebEngineWidgets")
        
    Returns:
        The imported module
    """
    full_module_name = f"{QT_BINDING}.Qt{module_name}"
    try:
        return importlib.import_module(full_module_name)
    except ImportError as e:
        warnings.warn(f"Could not import {full_module_name}: {e}")
        return None

# Provide consistent API for QApplication
def create_application(args: List[str] = None) -> QtWidgets.QApplication:
    """
    Create a QApplication with the appropriate settings for the current Qt binding.
    
    Args:
        args: Command line arguments to pass to the application
        
    Returns:
        A QApplication instance
    """
    if args is None:
        args = sys.argv
    
    app = QtWidgets.QApplication(args)
    return app

# Export commonly used classes with consistent API
class Color(QtGui.QColor):
    """Wrapper around QColor to ensure consistent API"""
    pass

class Font(QtGui.QFont):
    """Wrapper around QFont to ensure consistent API"""
    pass

# Mapping for classes that changed names or locations between versions
if QT_BINDING == 'PySide6':
    # PySide6-specific mappings
    from PySide6.QtCore import QSize, QPoint, QPointF, QRect, QRectF
    
    # Qt 6 has different packaging for OpenGL
    try:
        from PySide6.QtOpenGLWidgets import QOpenGLWidget
    except ImportError:
        QOpenGLWidget = None
    
    # Qt 6 moved some classes to different modules
    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView
    except ImportError:
        QWebEngineView = None
    
    # In Qt 6, QPrintDialog and related classes moved to a new module
    try:
        from PySide6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
    except ImportError:
        QPrinter = QPrintDialog = QPrintPreviewDialog = None
    
    # In Qt 6, SVG widgets are in a separate module
    try:
        from PySide6.QtSvgWidgets import QSvgWidget, QGraphicsSvgItem
    except ImportError:
        QSvgWidget = QGraphicsSvgItem = None

    # In Qt 6, QUndoCommand and related classes moved to QtGui
    from PySide6.QtGui import QUndoCommand, QUndoStack, QUndoGroup
        
elif QT_BINDING == 'PySide2':
    # PySide2-specific mappings
    from PySide2.QtCore import QSize, QPoint, QPointF, QRect, QRectF
    
    # Qt 5 uses QGLWidget for OpenGL
    try:
        from PySide2.QtOpenGL import QGLWidget as QOpenGLWidget
    except ImportError:
        QOpenGLWidget = None
    
    try:
        from PySide2.QtWebEngineWidgets import QWebEngineView
    except ImportError:
        QWebEngineView = None
    
    # In Qt 5, printing classes are in QtPrintSupport
    try:
        from PySide2.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
    except ImportError:
        QPrinter = QPrintDialog = QPrintPreviewDialog = None
    
    # In Qt 5, SVG widgets are part of QtSvg
    try:
        from PySide2.QtSvg import QSvgWidget, QGraphicsSvgItem
    except ImportError:
        QSvgWidget = QGraphicsSvgItem = None

    # In Qt 5, QUndoCommand and related classes are in QtWidgets
    from PySide2.QtWidgets import QUndoCommand, QUndoStack, QUndoGroup

# Container compatibility
# In Qt 6, QVector is now an alias for QList
# Define compatible list/vector classes
if QT_BINDING == 'PySide6':
    # In PySide6, QList and QVector are just Python lists
    # (QList was removed as a separate class)
    QList = list
    QVector = list
else:
    # In PySide2, keep the original Qt classes
    QList = getattr(QtCore, 'QList', list)
    QVector = getattr(QtCore, 'QVector', list)

# Additional compatibility mappings for specific modules
if QT_BINDING == 'PySide6':
    # PySide6-specific changes
    # QtCore changes
    QStringListModel = QtCore.QStringListModel
    
    # Qt 6 changed QTextCodec to QStringConverter
    try:
        QStringConverter = QtCore.QStringConverter
    except AttributeError:
        QStringConverter = None
    
    # Qt 6 introduced new input event classes
    QSinglePointEvent = QtGui.QSinglePointEvent if hasattr(QtGui, 'QSinglePointEvent') else None
    QPointingDevice = QtGui.QPointingDevice if hasattr(QtGui, 'QPointingDevice') else None
    
    # Use dict as QHash/QMultiHash in PySide6
    QHash = dict
    QMultiHash = dict
    
    # Qt 6 changed QDesktopWidget to QScreen-based API
    QScreen = QtGui.QScreen
    
    # Qt 6 compatibility for QQuickWindow
    try:
        QQuickGraphicsConfiguration = QtQuick.QQuickGraphicsConfiguration
        QQuickRenderTarget = QtQuick.QQuickRenderTarget
    except (AttributeError, ImportError):
        QQuickGraphicsConfiguration = None
        QQuickRenderTarget = None
    
    # Qt 6 QML changes
    QJSEngine = QtQml.QJSEngine
    QQmlEngine = QtQml.QQmlEngine
    try:
        QQmlListProperty = QtQml.QQmlListProperty  # Now uses qsizetype in Qt 6
    except AttributeError:
        QQmlListProperty = None
    
    # Qt 6 QML changes - QML property registration
    if hasattr(QtCore, 'QML_ELEMENT'):
        QML_ELEMENT = QtCore.QML_ELEMENT
        QML_SINGLETON = QtCore.QML_SINGLETON
        QML_ANONYMOUS = QtCore.QML_ANONYMOUS
        QML_INTERFACE = QtCore.QML_INTERFACE
    else:
        QML_ELEMENT = lambda: None
        QML_SINGLETON = lambda: None
        QML_ANONYMOUS = lambda: None
        QML_INTERFACE = lambda name=None: lambda: None
    
elif QT_BINDING == 'PySide2':
    # PySide2-specific changes
    QStringListModel = QtCore.QStringListModel
    
    # Qt 5 uses QTextCodec instead of QStringConverter
    QStringConverter = None
    
    # Qt 5 doesn't have these input event classes
    QSinglePointEvent = None
    QPointingDevice = None
    
    # Use dict as QHash/QMultiHash equivalent in PySide2
    QHash = dict
    QMultiHash = dict
    
    # In Qt 5, QColorSpace is not available in most installations
    if not hasattr(QtGui, 'QColorSpace'):
        QtGui.QColorSpace = type('QColorSpace', (), {})
    
    # QDesktopWidget in Qt 5
    try:
        QDesktopWidget = QtWidgets.QDesktopWidget
    except AttributeError:
        QDesktopWidget = None
    
    # Qt5 QScreen
    QScreen = QtGui.QScreen
    
    # QML in Qt5
    QJSEngine = QtQml.QJSEngine
    QQmlEngine = QtQml.QQmlEngine
    try:
        # QQmlListProperty is in QtCore for PySide2
        QQmlListProperty = QtCore.QQmlListProperty
    except AttributeError:
        try:
            # Fallback to QtQml for PySide6
            QQmlListProperty = QtQml.QQmlListProperty
        except AttributeError:
            QQmlListProperty = None
    
    # Dummy QML property registration for compatibility
    QML_ELEMENT = lambda: None
    QML_SINGLETON = lambda: None
    QML_ANONYMOUS = lambda: None
    QML_INTERFACE = lambda name=None: lambda: None

# Handle changes in how SQL query results are returned
def get_query_bound_values(query):
    """
    In Qt 6, QSqlQuery.boundValues() returns a dict instead of a list.
    This function provides a consistent interface.
    """
    if not hasattr(query, 'boundValues'):
        return {}
        
    result = query.boundValues()
    if QT_BINDING == 'PySide6':
        # In Qt 6, this already returns a dict
        return result
    else:
        # In Qt 5, convert the result to a dict
        if isinstance(result, list):
            return {i: val for i, val in enumerate(result)}
        return result

# Handle touch event changes between Qt 5 and Qt 6
def get_touch_points(touch_event):
    """
    Extract touch points from a touch event in a compatible way.
    In Qt 6, the API changed significantly for touch events.
    """
    if QT_BINDING == 'PySide6':
        return [point for point in touch_event.points()]
    else:
        return [point for point in touch_event.touchPoints()]
