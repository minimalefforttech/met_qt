# copyright (c) 2025 Alex Telford, http://minimaleffort.tech
import re
from typing import Optional
from met_qt._internal.qtcompat import QtCore

def get_metamethod(obj: QtCore.QObject, signal_or_slot) -> Optional[QtCore.QMetaMethod]:
    """Get the QMetaMethod of a signal in an object's meta-object
    eg:
        obj = QtCore.QObject()
        signal_method = get_metamethod(obj, obj.destroyed)
    """
    if match := re.search(r'SignalInstance (\w+)\(', repr(signal_or_slot)):
        # Signals aren't exposed to python, so we resolve it from the displayed signature.
        name = match.group(1)
        method_type = QtCore.QMetaMethod.MethodType.Signal
    elif hasattr(signal_or_slot, '__name__'):
        name = signal_or_slot.__name__
        method_type = QtCore.QMetaMethod.MethodType.Slot
    else:
        return None  # Likely not a signal
    
    meta_obj = obj.metaObject()
    if name.startswith('2'):  # Internally Qt prefixes slots and signals with 1 and 2.
        name = name[1:]
        
    for i in range(meta_obj.methodCount()):
        method = meta_obj.method(i)
        if not method.methodType() == method_type:
            continue
            
        if method.name().data().decode() == name:
            return method
    
    return None

def QProperty(name:str, type_, default=None, *, signal=False,
              converter=None, default_factory=None,
              variable_name=None, signal_name=None):
    """
    This function generates a QtCore.Property with customizable behavior, optionally with a change signal.
    Parameters:
        name (str): The name of the property, this must be the same as the variable you assign it to.
        type_: The type of the property
        default: The default value for the property (used if default_factory is None)
        signal (bool): If True, creates a signal that will be emitted when the property changes
        converter (callable): A function to convert the input value before storing (defaults to identity function)
        default_factory (callable): A function that returns the default value (takes precedence over default)
        variable_name (str): The name of the backing variable (defaults to "_" + name)
        signal_name (str): The name of the change signal (defaults to name + "Changed")
    Returns:
        If signal is True:
            tuple: (QtCore.Property, QtCore.Signal) - the property and its change signal
        If signal is False:
            QtCore.Property: the property
    Example:
        class MyClass(QObject):
            # Create a property with a change signal
            text, textChanged = QProperty("text", str, "", signal=True)
            # Create a property without a signal
            count = QProperty("count", int, 0)
    """
    variable_name = variable_name or f"_{name}"
    signal_name = signal_name or f"{name}Changed"
    converter = converter or (lambda x:x)
    def fget(self):
        if not hasattr(self, variable_name):
            setattr(self, variable_name, default_factory() if default_factory else default)
        return getattr(self, variable_name)
    
    def fset(self, value):
        value = converter(value)
        current = fget(self)
        if current == value:
            return
        setattr(self, variable_name, value)
        if signal:
            getattr(self, signal_name).emit(value)
    
    def freset(self):
        setattr(self, variable_name, default_factory() if default_factory else default)

    if signal:
        notifier = QtCore.Signal(type_, name=signal_name)
        prop = QtCore.Property(type_, fget, fset, freset, notify=notifier)
        return prop, notifier
    else:
        prop = QtCore.Property(type_, fget, fset, freset)
        return prop