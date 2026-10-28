"""Native query transforms retained only for the currently displayed frames."""

from anthroforge.native.scene import geometry_matrix


def key(row):
    return tuple(row["matrix"]), tuple(row["geometry_offset"])


class DisplayTransforms:
    def __init__(self):
        self.values = {}

    def retain(self, rows):
        current = {key(row) for row in rows}
        self.values = {k: v for k, v in self.values.items() if k in current}

    def matrix(self, engine, row):
        identity = key(row)
        if identity not in self.values:
            self.values[identity] = geometry_matrix(engine, *identity)
        return self.values[identity]
