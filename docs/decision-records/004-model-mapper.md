# 004-model-mapper

## Stakeholders
Alex Telford

## Status
Completed

## Context

In order to facilitate mapping data from a model to widgets we use s QDataWidgetMapper, however this does not work for user data.

## Decision

Introduce a `ModelDataMapper` class to provide flexible, two-way data binding between a model usre data and arbitrary widget properties. This mapper supports custom setter and extractor functions, arbitrary roles, and automatic or manual commit of changes. It manages signal connections for two-way synchronization and is designed to work with any QObject-based widget or object.

## Consequences

- Simplifies the implementation of editable forms and property editors.
- Reduces boilerplate code for synchronizing model and widget data.
- Enables custom mapping logic for complex data types or widget behaviors.
- Requires careful management of signal connections and memory (handled via weak references).
- Additional overhead for maintaining mappers
- Additional overhead for objects that are removed out of turn

## Related ADRs
- 002-bindings: General approach to data binding in the codebase.

## Example Usage

```python
mapper = ModelDataMapper()
mapper.set_model(model)
mapper.add_mapping(
    spinbox, "value", role=QtCore.Qt.UserRole,
    fn_set=lambda w, d: w.setValue(d.get("quantity", 0)),
    fn_extract=lambda w, d: {**d, "quantity": w.value()},
    signal=spinbox.valueChanged
)
mapper.set_current_index(0)
```

This enables two-way synchronization between the model and the widget, with support for custom logic and roles.
