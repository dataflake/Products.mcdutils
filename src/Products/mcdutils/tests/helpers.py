""" Unit test helper modules """


class DummyMemcache(dict):

    def _assertKeyBinary(self, key):
        if not isinstance(key, str):
            raise ValueError('Key must be binary string.')
        return key

    def set(self, key, value):
        self._assertKeyBinary(key)
        self[key] = value
        return True

    def add(self, key, value):
        self._assertKeyBinary(key)
        if key not in self:
            self[key] = value
            return True

    def replace(self, key, value):
        self._assertKeyBinary(key)
        if key in self:
            self[key] = value
            return True

    def delete(self, key, time=0):
        self._assertKeyBinary(key)
        if key in self:
            del self[key]
            return True

    def get(self, key):
        self._assertKeyBinary(key)
        if key in self:
            return self[key]

    def get_multi(self, keys):
        res = {}
        for key in keys:
            self._assertKeyBinary(key)
            res[key] = self.get(key)
        return res
