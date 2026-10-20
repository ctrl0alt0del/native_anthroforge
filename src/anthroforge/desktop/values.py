"""Convert immutable application values at the Qt adapter boundary."""

import numpy as np


def qml(value):
    if isinstance(value, np.generic):
        return qml(value.item())
    if isinstance(value, dict):
        return {key: qml(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [qml(item) for item in value]
    return value
