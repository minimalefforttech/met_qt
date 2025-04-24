# copyright (c) 2025 Alex Telford, http://minimaleffort.tech
import uuid
from typing import Any, Callable, List
from dataclasses import dataclass
from met_qt._internal.qtcompat import QtCore

class SimpleBinding:
    """Manages a one-way binding from a source property to one or more target properties"""
    def __init__(self, source: QtCore.QObject, source_property: str):
        self._uuid = uuid.uuid4()
        self._source = source
        self._source_property = source_property
        self._targets = []
    
    def to(self, target: QtCore.QObject, target_property: str, converter=None):
        """Add a target property to this binding"""
        self._targets.append((target, target_property, converter))
        return self
    
    def update_targets(self):
        """Update all target properties with the current source value"""
        if not self._source:
            return
            
        # Special handling for QSpinBox value
        if self._source_property == "value" and hasattr(self._source, "value"):
            source_value = self._source.value()
        else:
            source_value = self._source.property(self._source_property)
        
        for target, target_property, converter in self._targets:
            if not target:
                continue
                
            try:
                value = converter(source_value) if converter else source_value
                current_value = target.property(target_property)
            except Exception as e:
                print(f"SimpleBinding: Error converting value: {e}")
                return
            
            if current_value == value:
                continue
                
            if isinstance(current_value, float) and isinstance(value, float):
                if abs(current_value - value) <= 1e-9 * max(abs(current_value), abs(value)):
                    continue
                    
            target.setProperty(target_property, value)

    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
