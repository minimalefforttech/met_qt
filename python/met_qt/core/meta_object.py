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