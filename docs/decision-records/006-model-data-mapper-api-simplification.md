# 006-model-data-mapper-api-simplification

## Status
Implemented

## Context

The original `ModelDataMapper.add_mapping` API used `fn_set` and `fn_extract` to customize how data is transferred between the model and the widget property. This was flexible but the naming was not intuitive and did not clearly express the direction of data flow. Additionally, the signatures required both the widget and the model data, which was sometimes awkward for simple cases.

## Decision

- Replace `fn_set` and `fn_extract` in `add_mapping` with two new callables:
  - `from_model(model_data) -> value`: Converts model data to the value to set on the widget property. Default: returns `model_data`.
  - `from_property(value, model_data) -> new_model_data`: Converts the property value (and current model data) to the new model data to store in the model. Default: returns `value`.
- Update all usages and documentation to use the new API.
- This change makes the direction of data flow explicit and simplifies the most common cases.

## Consequences

- The API is more intuitive and easier to use for both simple and advanced mappings.
- Existing code using `fn_set`/`fn_extract` must be updated to use `from_model`/`from_property`.
- The new API is more consistent with other binding patterns in the codebase.

## Example (after)

```python
mapper.add_mapping(
    spinbox, "value", role=QtCore.Qt.UserRole,
    from_model=lambda d: d.get("quantity", 0),
    from_property=lambda v, d: {**d, "quantity": v},
    signal=spinbox.valueChanged
)
```

---
Date: 2025-04-26
Status: Implemented
