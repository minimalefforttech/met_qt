# ADR 002: Property Bindings System

## Stakeholders
Alex Telford

## Status
Completed

## Context and Motivation

I require a way to simplify property bindings across components, particularly for bidirectional bindings or expression based bindings.

## Decision

We will implement a core bindings manager (`Bindings` class) in `met_qt.core.binding`. This system supports:

- **One-way bindings**: Synchronize a source property to one or more targets, optionally with a converter.
- **Two-way (group) bindings**: Keep multiple properties in sync bidirectionally.
- **Expression bindings**: Bind a target property to an expression involving multiple sources.

Bindings are managed centrally, with automatic observation of property changes via Qt signals, event filters, and dynamic property change events.

## Implementation Details

- The `Bindings` class manages all active bindings and observed objects.
- One-way bindings are created with `bind(source, property)`, returning a `SimpleBinding` that can be chained with `.to(target, property, converter)`.
- Two-way bindings use `bind_group()`, returning a `GroupBinding` to which properties can be added.
- Expression bindings use `bind_expression(target, property, expression_str)`, supporting variable binding from multiple sources, this is done with a context manager.
- Property changes are detected using Qt's notify signals, custom signals, or event filters for dynamic properties and special events.
- Special handling is implemented for Qt widgets that require direct method calls (e.g., QSpinBox's value() method) instead of property() access.
- Callbacks can be registered for property changes, supporting custom reactions beyond value synchronization.
- The system cleans up bindings and observers when objects are destroyed.

## Example Usage

```
from met_qt.core.binding import Bindings
# ... Qt widget setup ...
bindings = Bindings(self)

# One-way binding: spinbox -> label
bindings.bind(spinbox, "value").to(value_label, "text", lambda x: f"Value: {int(x)}")

# Two-way binding between line edits
group = bindings.bind_group()
group.add(edit1, "text")
group.add(edit2, "text")

# Expression binding: combine first and last names
with bindings.bind_expression(full_name, "text", "{first} {last}") as expr:
    expr.bind("first", first_name, "text")
    expr.bind("last", last_name, "text")
```

## Consequences

- The bindings system reduces boilerplate and improves maintainability for property synchronization in Qt UIs.
- It supports advanced scenarios (expressions, dynamic properties, event-based updates) while remaining easy to use for common cases.
- The binding layer introduces a degree of overhead that is unsuitable for scaled applications in python.

---
Date: 2025-04-24
Status: Implemented
