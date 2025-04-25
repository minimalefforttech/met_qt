# 5. Float and Range Sliders

## Status
Completed

## Stakeholders
Alex Telford

## Context
We need float value sliders that have
- Floating-point values with arbitrary precision
- Hard and soft value ranges
- Single value (FloatSlider) and range (RangeSlider) selection
- Native Qt look and feel
- Qt 5/6 compatibility

## Decision
Two slider widget classes have been implemented:

### 1. FloatSlider
A single-handle slider supporting floating-point values with:
- Hard range: Absolute minimum and maximum values that cannot be exceeded
- Soft range: Tha displayed range, this extends up to hard range if value is set outside tha range but within the hard range.
- Interactive range: Dynamic intersection of soft and hard ranges
- Configurable step sizes and decimal precision
- Native Qt styling through QStylePainter

### 2. RangeSlider
A dual-handle slider for selecting value ranges with:
- Two handles for minimum and maximum value selection
- Handles can pass each other (swapping min/max roles)
- Soft range support matching FloatSlider
- Custom painting with Qt native handle appearance because style painter draws line from 0 which is not valid here.

### Common Features
Both sliders share:
- Qt 5/6 compatibility through qtcompat layer
- Mouse and keyboard interaction support
- Value clamping and step size enforcement
- Signal emission for value changes and slider events
- Integration with met_qt binding system
- Inheritance from AbstractSoftSlider for shared functionality

## Consequences

### Advantages
1. Flexible range control
   - Hard limits for absolute boundaries
   - Soft limits for non default but still valid ranges

2. Developer Benefits
   - Property API for basic usage
   - Consistent behavior across Qt versions

### Challenges
Custom painting complexity in RangeSlider
QStylePainter cannot draw the groove without putting a highlight blob at 0


## Notes
- The widgets are demonstrated in slider_examples.py
- Future improvements could include:
  - Support for non-linear values
  - Tick mark customization
  - Inner and outer range option
