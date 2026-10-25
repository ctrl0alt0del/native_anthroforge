"""Ordered object selection for construction input; component selection stays separate."""


class ObjectSelection:
    def __init__(self):
        self.items = []

    @property
    def primary(self):
        return self.items[-1] if self.items else ""

    def choose(self, identity, extend=False):
        if not extend:
            self.items = [identity] if identity else []
        elif identity in self.items:
            self.items.remove(identity)
        elif identity:
            self.items.append(identity)

    def retain(self, identities):
        self.items = [key for key in self.items if key in identities]

    def replace(self, identities):
        self.items = list(dict.fromkeys(key for key in identities if key))
