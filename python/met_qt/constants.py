# copyright (c) 2025 Alex Telford, http://minimaleffort.tech

# Qt properties that are affected by events rather than signals.
EVENT_PROPERTIES = (
    "pos", "geometry", "size", "rect", "minimumSize", "maximumSize",
    "sizePolicy", "sizeIncrement", "baseSize", "palette"
)