


class Key_Events:
    def __init__(self):
        self.key = ''
    def key_pressed(self, key):
        self.key = key
    def get_key(self):
        k = self.key
        self.key = ''
        return k
