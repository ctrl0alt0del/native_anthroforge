"""Convert immutable application values at the Qt adapter boundary."""


def qml(value):
    if isinstance(value, dict):
        return {key: qml(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [qml(item) for item in value]
    return value
