# copyright (c) 2025 Alex Telford, http://minimaleffort.tech

from weakref import ref as weakref
from met_qt._internal.qtcompat import Shiboken, QtCore
from .meta import QProperty

class ModelDataMapper(QtCore.QObject):
    """
    Maps data between a QAbstractItemModel and UI widgets or objects, supporting arbitrary roles and two-way mapping.

    This class allows you to bind properties of widgets (or other QObject-based objects) to data in a model, with support for custom setter and extractor functions, and optional auto-commit of changes. It manages signal connections for two-way data synchronization and can be used to implement editable forms or views that reflect and update model data.

    Attributes:
        auto_commit (QProperty): If True, changes are immediately committed to the model; otherwise, they are batched until commit() is called.
    """
    auto_commit = QProperty("auto_commit", bool, default=True, signal=False)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = None
        self._mappings = {}
        self._current_index = 0
        self._in_update = False
        self._pending_commits = set()

    def commit(self):
        """
        Push all pending changes from mapped widgets/objects to the model.

        If auto_commit is False, this method must be called to write changes back to the model.
        """
        if not self._model:
            return
        for mapping in list(self._pending_commits):
            target = mapping['target_ref']()
            if target is None or (Shiboken and not Shiboken.isValid(target)):
                continue
            idx = self._get_index(mapping['section'])
            old_data = self._model.data(idx, mapping['role'])
            new_data = mapping['fn_extract'](target, old_data)
            if new_data != old_data:
                self._model.setData(idx, new_data, mapping['role'])
        self._pending_commits.clear()

    def add_mapping(self, target, property_name, section=0, role=QtCore.Qt.DisplayRole, fn_set=None, fn_extract=None, signal=None):
        """
        Add a mapping between a widget/object property and a model data role.

        Args:
            target (QObject): The widget or object to map.
            property_name (str): The property name on the target to bind.
            section (int): The model column/section to map (default: 0).
            role (int): The Qt item data role to use (default: DisplayRole).
            fn_set (callable): Function to set the property from model data (optional).
            fn_extract (callable): Function to extract data from the property (optional).
            signal (QtCore.Signal): Signal to connect for change notification (optional).
        """
        # Default setter: obj.setProperty(property_name, data)
        if fn_set is None:
            def fn_set(obj, data):
                obj.setProperty(property_name, data)
        # Default extractor: obj.property(property_name)
        if fn_extract is None:
            def fn_extract(obj, data):
                return obj.property(property_name)
        target_ref = weakref(target)
        notify_signal = self._find_notify_signal(target, property_name)
        if notify_signal is None and signal is not None:
            notify_signal = signal
        mapping = {
            'target_ref': target_ref,
            'property_name': property_name,
            'section': section,
            'role': role,
            'fn_set': fn_set or (lambda obj, data: obj.setProperty(property_name, data)),
            'fn_extract': fn_extract or (lambda obj, data: obj.property(property_name)),
            'signal': notify_signal
        }
        # Use the weakref object itself as the key (unique per obj instance)
        self._mappings[target_ref] = mapping
        if notify_signal is not None:
            notify_signal.connect(self._apply_to_model)

    def set_model(self, model):
        """
        Set the model to be mapped and refresh all mappings.

        Args:
            model (QAbstractItemModel): The model to use.
        """
        self._model = model
        self._current_index = None
        self.refresh()

    def set_current_index(self, index):
        """
        Set the current row/section index for mapping.

        Args:
            index (int or QModelIndex): The row index or QModelIndex to use.
        """
        if self._pending_commits:
            self.commit()
        if isinstance(index, QtCore.QModelIndex):
            self._current_index = QtCore.QPersistentModelIndex(index)
        else:
            # Accept row int for convenience (first column)
            if self._model is not None:
                idx = self._model.index(index, 0)
                self._current_index = QtCore.QPersistentModelIndex(idx)
            else:
                self._current_index = None
        self.refresh()

    def _get_index(self, section):
        """
        Get the QModelIndex for the current row and given section/column.

        Args:
            section (int): The column/section index.
        Returns:
            QModelIndex: The corresponding model index.
        """
        if self._current_index is None or not self._current_index.isValid():
            return QtCore.QModelIndex()
        return self._current_index.sibling(self._current_index.row(), section)

    def _apply_to_model(self):
        """
        Slot to apply changes from a mapped widget/object to the model when its value changes.
        """
        if self._in_update:
            return
        sender = self.sender()
        if sender is None:
            return
        mapping = None
        for ref, m in self._mappings.items():
            target = ref()
            if target is sender:
                mapping = m
                break
        if not mapping:
            return
        target = mapping['target_ref']()
        if target is None or (Shiboken and not Shiboken.isValid(target)):
            return
        if not self._model:
            return
        idx = self._get_index(mapping['section'])
        old_data = self._model.data(idx, mapping['role'])
        new_data = mapping['fn_extract'](target, old_data)
        if new_data != old_data:
            if self.auto_commit:
                self._in_update = True
                self._model.setData(idx, new_data, mapping['role'])
                self._in_update = False
            else:
                self._pending_commits.add(mapping)

    def refresh(self):
        """
        Update all mapped widgets/objects from the current model data.
        """
        if not self._model:
            return
        for mapping in self._mappings.values():
            target = mapping['target_ref']()
            if target is None or (Shiboken and not Shiboken.isValid(target)):
                continue
            idx = self._get_index(mapping['section'])
            data = self._model.data(idx, mapping['role'])
            self._in_update = True
            mapping['fn_set'](target, data)
            self._in_update = False

    def _find_notify_signal(self, obj, property_name):
        """
        Find the notify signal for a given property on a QObject, if available.

        Args:
            obj (QObject): The object to inspect.
            property_name (str): The property name.
        Returns:
            QtCore.Signal or None: The notify signal, or None if not found.
        """
        meta = obj.metaObject()
        prop_idx = meta.indexOfProperty(property_name)
        if prop_idx < 0:
            return None
        prop = meta.property(prop_idx)
        if prop.hasNotifySignal():
            return getattr(obj, prop.notifySignal().name().data().decode(), None)
        return None

    def clear(self):
        """
        Remove all mappings and disconnect any connected signals.
        """
        for mapping in self._mappings.values():
            signal = mapping.get('signal')
            if signal is not None:
                try:
                    signal.disconnect(self._apply_to_model)
                except Exception:
                    pass
        self._mappings.clear()
