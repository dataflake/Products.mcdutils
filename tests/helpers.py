##############################################################################
#
# Copyright (c) 2008-2023 Tres Seaver and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
#############################################################################


class DummyMemcache(dict):
    def _assertKeyBinary(self, key):
        if not isinstance(key, bytes):
            raise ValueError("Key must be binary string.")
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
