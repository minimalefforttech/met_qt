# copyright (c) 2025 Alex Telford, http://minimaleffort.tech
from __future__ import annotations
from typing import Any, Callable, List
from met_qt._internal.qtcompat import QtCore
from .structs import Converter, BoundProperty

class GroupBinding:
    """Manages bidirectional bindings between multiple properties"""
    def __init__(self, bindings_manager, initial_value=None):
        self._bindings_manager = bindings_manager
        self._properties: List[BoundProperty] = []
        self._normalized_value = initial_value
        self._updating = False
        
    def add(self, obj: QtCore.QObject, property_name: str, 
            to_normalized: Callable[[Any], Any] = None,
            from_normalized: Callable[[Any], Any] = None) -> GroupBinding:
        """Add a property to the binding group with optional converter functions"""
        converter = Converter()
        if to_normalized:
            converter.to_normalized = to_normalized
        if from_normalized:
            converter.from_normalized = from_normalized
            
        bound_prop = BoundProperty(obj, property_name, converter)
        self._properties.append(bound_prop)
        
        self._bindings_manager._connect_to_property_changes(
            obj, property_name, lambda: self._on_property_changed(bound_prop))
        
        if self._normalized_value is not None:
            self._update_property(bound_prop)
        elif self._properties and len(self._properties) == 1:
            self._normalized_value = bound_prop.converter.to_normalized(
                obj.property(property_name)
            )
            
        return self
    
    def _on_property_changed(self, source_prop: BoundProperty):
        """Handle property change events from any bound property"""
        if self._updating:
            return
            
        try:
            self._updating = True
            new_value = source_prop.converter.to_normalized(
                source_prop.obj.property(source_prop.property_name)
            )
            self._normalized_value = new_value
            
            for prop in self._properties:
                if prop is not source_prop:
                    self._update_property(prop)
        finally:
            self._updating = False
    
    def _update_property(self, prop: BoundProperty):
        """Update a bound property with the current normalized value"""
        if self._normalized_value is None:
            return
            
        converted_value = prop.converter.from_normalized(self._normalized_value)
        prop.obj.setProperty(prop.property_name, converted_value)
        
    def update_value(self, value):
        """Manually update the normalized value and all properties"""
        if self._updating:
            return
            
        try:
            self._updating = True
            self._normalized_value = value
            
            for prop in self._properties:
                self._update_property(prop)
        finally:
            self._updating = False

    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False