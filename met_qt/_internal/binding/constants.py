# copyright (c) 2025 Alex Telford, http://minimaleffort.tech
from enum import IntFlag, auto
from typing import Dict
from met_qt._internal.qtcompat import QtCore

class EventInterest(IntFlag):
    """Flags indicating what types of events a binding is interested in."""
    NONE = 0
    DYNAMIC_PROPERTY = auto()
    GEOMETRY = auto()
    STATE = auto()
    STYLE = auto()

# Mapping of property names to their corresponding event interests
PROPERTY_EVENT_MAPPING: Dict[str, EventInterest] = {
    "pos": EventInterest.GEOMETRY,
    "geometry": EventInterest.GEOMETRY,
    "size": EventInterest.GEOMETRY,
    "rect": EventInterest.GEOMETRY,
    "minimumSize": EventInterest.GEOMETRY,
    "maximumSize": EventInterest.GEOMETRY,
    "sizePolicy": EventInterest.GEOMETRY,
    "sizeIncrement": EventInterest.GEOMETRY,
    "baseSize": EventInterest.GEOMETRY,
    "palette": EventInterest.STYLE,
    "font": EventInterest.STYLE,
    "enabled": EventInterest.STATE,
    "visible": EventInterest.STATE,
    "focus": EventInterest.STATE,
}

# Mapping of Qt events to their corresponding event interests
EVENT_TO_INTEREST: Dict[QtCore.QEvent.Type, EventInterest] = {
    QtCore.QEvent.DynamicPropertyChange: EventInterest.DYNAMIC_PROPERTY,
    QtCore.QEvent.Move: EventInterest.GEOMETRY,
    QtCore.QEvent.Resize: EventInterest.GEOMETRY,
    QtCore.QEvent.LayoutRequest: EventInterest.GEOMETRY,
    QtCore.QEvent.ShowToParent: EventInterest.STATE,
    QtCore.QEvent.HideToParent: EventInterest.STATE,
    QtCore.QEvent.EnabledChange: EventInterest.STATE,
    QtCore.QEvent.FontChange: EventInterest.STYLE,
    QtCore.QEvent.StyleChange: EventInterest.STYLE,
    QtCore.QEvent.PaletteChange: EventInterest.STYLE,
}
