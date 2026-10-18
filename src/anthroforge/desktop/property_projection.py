"""Stable read-only QML properties; immutable values drive field-level notifications."""

from dataclasses import asdict, fields, is_dataclass

from PySide6.QtQml import QQmlPropertyMap

from anthroforge.core.construction import Curve

from .values import qml


def members(value):
    if is_dataclass(value):
        data = {f.name: getattr(value, f.name) for f in fields(value)}
        if isinstance(value, Curve):
            data.update(engine=value.engine, resolution=value.resolution)
        return data
    return value


def plain(value):
    if is_dataclass(value):
        return qml(asdict(value))
    if isinstance(value, (list, tuple)):
        return [plain(item) for item in value]
    if isinstance(value, dict):
        return {key: plain(item) for key, item in value.items()}
    return value


class PropertyProjection(QQmlPropertyMap):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._values, self._children = {}, {}
        self._source = None

    def updateValue(self, key, value):
        return self.value(key)  # UI mutations must use application commands.

    def get(self, key, default=None):
        return plain(self._values.get(key, default))

    def __getitem__(self, key):
        return plain(self._values[key])

    def __bool__(self):
        return bool(self._values)

    def as_dict(self):
        return plain(self._values)

    def synchronize(self, source):
        if source is self._source:
            return
        values = members(source)
        for key in self._values.keys() - values.keys():
            self.insert(key, None)
        for key, value in values.items():
            if key not in self._values or value is not self._values[key]:
                self.update_field(key, value)
        self._source, self._values = source, dict(values)
        self.release_children(values)

    def update_field(self, key, value):
        adapted = self.adapt(key, value)
        if not self.contains(key) or self.value(key) != adapted:
            self.insert(key, adapted)

    def adapt(self, key, value):
        if is_dataclass(value) or isinstance(value, dict):
            child = self._children.setdefault(key, None)
            if child is None:
                child = self._children[key] = PropertyProjection(self)
            child.synchronize(value)
            return child
        if isinstance(value, (list, tuple)) and value and record_id(value[0]) is not None:
            return [self.adapt((key, record_id(item)), item) for item in value]
        return qml(value)

    def release_children(self, values):
        wanted = set(values)
        for key, value in values.items():
            if isinstance(value, (list, tuple)):
                wanted.update((key, record_id(item)) for item in value)
        for key in self._children.keys() - wanted:
            self._children.pop(key).deleteLater()


def record_id(value):
    return value.get("id") if isinstance(value, dict) else getattr(value, "id", None)
