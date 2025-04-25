# ADR 003: BoxPaintLayout for Paint-Based Layouts

## Stakeholders
Alex Telford

## Status
Completed

## Context and Motivation

In some scenarios, we need to lay out items inside a paint event where using QWidget-based objects is not appropriate or possible. A common example is within a QStyledItemDelegate, where the painting is handled directly and widget instantiation is not feasible. While QGraphicsScene provides a flexible scene graph for painting and interaction, it is too heavyweight for these use cases.

## Decision

We introduce `BoxPaintLayout`, a lightweight layout manager that can be used within paint events. This class mimics the API of standard Qt layouts but is designed for use in custom painting contexts. It supports:

- Arranging and sizing paintable items (boxes, text, paths) without requiring QWidget instances.
- Minimal interactive features: hover and click support for painted items.
- Integration with standard Qt layouts for hybrid widget/painted UIs.

`BoxPaintLayout` is implemented in `met_qt.gui.paint_layout` and is used in places where widget-based layouts are not suitable but a full scene graph is unnecessary.

## Consequences

- Enables complex, interactive painted layouts in delegates and custom widgets without the overhead of QGraphicsScene or QWidget hierarchies.
- Maintains a familiar layout API for developers already using Qt layouts.
- Keeps the codebase lightweight and maintainable for paint-based UIs.
- Only minimal interactivity (hover, click) is supported; advanced event handling or animations should use QGraphicsScene or custom solutions.

---
Date: 2025-04-24
Status: Implemented
