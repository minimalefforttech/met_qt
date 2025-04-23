# copyright (c) 2025 Alex Telford, http://minimaleffort.tech
from typing import Dict, Any, Tuple, List, Callable, Set, Optional
import uuid
import re

from met_qt import constants
from met_qt._internal.qtcompat import QtCore

from met_qt._internal import binding as _binding
from .meta_object import get_metamethod as _get_metamethod


class Bindings(QtCore.QObject):
    """Core manager class for property bindings"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._bindings: Dict[uuid.UUID, _binding.Binding] = {}
        self._observed_objects = set()
        self._signal_to_binding: Dict[Tuple[QtCore.QObject, int], uuid.UUID] = {}
        self._object_event_interest: Dict[QtCore.QObject, _binding.constants.EventInterest] = {}
        self._object_dynamic_properties: Dict[QtCore.QObject, Set[str]] = {}
        self._property_callbacks: Dict[Tuple[QtCore.QObject, str], List[Callable]] = {}
    
    def bind(self, source: QtCore.QObject, source_property: str, signal=None) -> _binding.SimpleBinding:
        """Create a one-way binding from a source property"""
        binding = _binding.SimpleBinding(source, source_property)
        self._bindings[binding._uuid] = binding
        
        signal_idx = self._setup_property_observation(source, source_property, signal)
        
        if signal_idx != -1:
            self._signal_to_binding[(source, signal_idx)] = binding._uuid
        
        return binding
    
    def bind_group(self, initial_value=None) -> _binding.GroupBinding:
        """Create a new binding group for bidirectional binding"""
        return _binding.GroupBinding(self, initial_value)
    
    def bind_expression(self, target: QtCore.QObject, target_property: str, 
                       expression_str: str, converter: Callable = None) -> _binding.ExpressionBinding:
        """Create a binding from an expression to a target property"""
        binding = _binding.ExpressionBinding(self, target, target_property, expression_str, converter)
        return binding
        
    @QtCore.Slot()
    def _source_destroyed(self):
        """Handle destruction of bound objects"""
        object = self.sender()
        if not object:
            return
        self._remove_bindings_for_object(object)

    @QtCore.Slot()
    def _property_changed(self):
        """Handle property change notifications"""
        sender_obj = self.sender()
        signal_idx = self.senderSignalIndex()
        
        if not sender_obj:
            return
            
        key = (sender_obj, signal_idx)
        if key in self._signal_to_binding:
            binding_id = self._signal_to_binding[key]
            self._update_binding(binding_id)
        
        self._trigger_property_callbacks(sender_obj)
    
    def _trigger_property_callbacks(self, obj: QtCore.QObject):
        """Trigger callbacks for property changes"""
        meta_obj = obj.metaObject()
        signal_idx = self.senderSignalIndex()
        
        for i in range(meta_obj.propertyCount()):
            prop = meta_obj.property(i)
            if prop.hasNotifySignal() and prop.notifySignalIndex() == signal_idx:
                prop_name = prop.name()
                key = (obj, prop_name)
                if key in self._property_callbacks:
                    for callback in self._property_callbacks[key]:
                        callback()
                break
                
    def _setup_property_observation(self, obj: QtCore.QObject, property_name: str, 
                                   signal: Optional[QtCore.Signal] = None) -> int:
        """Setup property observation for an object and return the signal index if connected"""
        signal_idx = -1
        
        if obj not in self._observed_objects:
            obj.installEventFilter(self)
            obj.destroyed.connect(self._source_destroyed)
            self._observed_objects.add(obj)
            self._object_event_interest[obj] = _binding.constants.EventInterest.NONE
            self._object_dynamic_properties[obj] = set()
        
        meta_obj = obj.metaObject()
        meta_property = None
        property_index = meta_obj.indexOfProperty(property_name)
        
        if property_index >= 0:
            meta_property = meta_obj.property(property_index)
        
        if signal:
            signal.connect(self._property_changed)
            meta_method = _get_metamethod(obj, signal)
            signal_idx = meta_obj.indexOfSignal(meta_method.methodSignature().data().decode())
        elif meta_property and meta_property.hasNotifySignal():
            notify_signal = meta_property.notifySignal()
            notifier = getattr(obj, str(notify_signal.name(), 'utf-8'))
            notifier.connect(self._property_changed)
            meta_method = _get_metamethod(obj, notifier)
            signal_idx = meta_obj.indexOfSignal(meta_method.methodSignature().data().decode())
        elif property_name in constants.EVENT_PROPERTIES:
            event_interest = _binding.constants.PROPERTY_EVENT_MAPPING.get(property_name, _binding.constants.EventInterest.NONE)
            self._object_event_interest[obj] |= event_interest
        else:
            self._object_event_interest[obj] |= _binding.constants.EventInterest.DYNAMIC_PROPERTY
            self._object_dynamic_properties[obj].add(property_name)
        
        return signal_idx
    
    def _connect_to_property_changes(self, obj: QtCore.QObject, property_name: str, 
                                     callback: Callable[[], None]):
        """Connect to property change notifications for an object"""
        key = (obj, property_name)
        if key not in self._property_callbacks:
            self._property_callbacks[key] = []
        
        self._property_callbacks[key].append(callback)
        
        self._setup_property_observation(obj, property_name)

    def _update_binding(self, binding_id: uuid.UUID):
        """Update a binding's targets with the current source value"""
        if binding_id in self._bindings:
            self._bindings[binding_id].update_targets()
            
    def _remove_bindings_for_object(self, obj: QtCore.QObject):
        """Remove all bindings associated with an object"""
        self._observed_objects.discard(obj)
        self._object_event_interest.pop(obj, None)
        self._object_dynamic_properties.pop(obj, None)
        
        to_remove = []
        for binding_id, binding in self._bindings.items():
            if binding._source == obj:
                to_remove.append(binding_id)
            else:
                binding._targets = [(target, prop, conv) for target, prop, conv in binding._targets 
                                if target != obj]
                
        for binding_id in to_remove:
            self._bindings.pop(binding_id, None)
            
        keys_to_remove = []
        for key in self._signal_to_binding:
            sender, _ = key
            if sender == obj:
                keys_to_remove.append(key)
                
        for key in keys_to_remove:
            self._signal_to_binding.pop(key, None)
            
        keys_to_remove = []
        for key in self._property_callbacks:
            callback_obj, _ = key
            if callback_obj == obj:
                keys_to_remove.append(key)
                
        for key in keys_to_remove:
            self._property_callbacks.pop(key, None)
            
    def eventFilter(self, obj: QtCore.QObject, event: QtCore.QEvent) -> bool:
        """Filter events for bound objects"""
        if obj not in self._object_event_interest:
            return False
            
        interest = self._object_event_interest.get(obj, _binding.constants.EventInterest.NONE)
        if interest == _binding.constants.EventInterest.NONE:
            return False
            
        event_type = event.type()
        event_interest = _binding.constants.EVENT_TO_INTEREST.get(event_type, _binding.constants.EventInterest.NONE)
        
        if event_interest == _binding.constants.EventInterest.NONE:
            return False
            
        if not (interest & event_interest):
            return False
            
        if event_type == QtCore.QEvent.DynamicPropertyChange:
            property_name = event.propertyName().data().decode()
            if property_name in self._object_dynamic_properties.get(obj, set()):
                for binding_id, binding in self._bindings.items():
                    if binding._source == obj and binding._source_property == property_name:
                        self._update_binding(binding_id)
        
        else:
            for binding_id, binding in self._bindings.items():
                if binding._source == obj:
                    property_interest = _binding.constants.PROPERTY_EVENT_MAPPING.get(binding._source_property, _binding.constants.EventInterest.NONE)
                    if property_interest & event_interest:
                        self._update_binding(binding_id)
        
        if event_type == QtCore.QEvent.DynamicPropertyChange:
            property_name = event.propertyName().data().decode()
            key = (obj, property_name)
            if key in self._property_callbacks:
                for callback in self._property_callbacks[key]:
                    callback()
        elif event_interest != _binding.constants.EventInterest.NONE:
            for prop_name, prop_interest in _binding.constants.PROPERTY_EVENT_MAPPING.items():
                if prop_interest & event_interest:
                    key = (obj, prop_name)
                    if key in self._property_callbacks:
                        for callback in self._property_callbacks[key]:
                            callback()
        
        return super().eventFilter(obj, event)

