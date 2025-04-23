# copyright (c) 2025 Alex Telford, http://minimaleffort.tech
from typing import Any, Callable, List
from dataclasses import dataclass
from met_qt._internal.qtcompat import QtCore

@dataclass
class Converter:
    """Represents bidirectional value converters for a property"""
    to_normalized: Callable[[Any], Any] = lambda x: x
    from_normalized: Callable[[Any], Any] = lambda x: x

@dataclass
class BoundProperty:
    """Represents a property that participates in a bidirectional binding group"""
    obj: QtCore.QObject
    property_name: str
    converter: Converter = None
    
    def __post_init__(self):
        if self.converter is None:
            self.converter = Converter()