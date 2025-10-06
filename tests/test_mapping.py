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

import contextlib


class TestMemCacheMappingSavepoint:
    def _getTargetClass(self):
        from Products.mcdutils.mapping import MemCacheMappingSavepoint

        return MemCacheMappingSavepoint

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()()

    def test_conforms_to_IDataManagerSavepoint(self):
        from transaction.interfaces import IDataManagerSavepoint
        from zope.interface.verify import verifyClass

        verifyClass(IDataManagerSavepoint, self._getTargetClass())

    def test_rollback(self):
        # This doesn't really do anything. Just verifying the
        # method is there and doesn't blow up when called.
        sp = self._makeOne()
        assert not sp.rollback()


class TestMemCacheMapping:
    def _getTargetClass(self):
        from Products.mcdutils.mapping import MemCacheMapping

        return MemCacheMapping

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_conforms_to_ISavepointDataManager(self):
        from transaction.interfaces import ISavepointDataManager
        from zope.interface.verify import verifyClass

        verifyClass(ISavepointDataManager, self._getTargetClass())

    def test___setitem___triggers_register(self):
        mapping = self._makeOne("key", DummyProxy())
        assert not mapping._p_changed
        assert not mapping._p_joined
        mapping["abc"] = 123
        assert mapping._p_changed
        assert mapping._p_joined

    def test_has_key(self):
        # Added in for backwards-compatibility under Python 3
        mapping = self._makeOne("key", DummyProxy())

        assert not mapping.has_key("foo")
        mapping["foo"] = "bar"
        assert mapping.has_key("foo")

    def test__getstate__and__setstate__(self):
        mapping = self._makeOne("key", DummyProxy())

        assert mapping.__getstate__() == {}
        mapping.__setstate__({"foo": "bar"})
        assert mapping.__getstate__() == {"foo": "bar"}

    def test_getContainerKey(self):
        mapping = self._makeOne("key", DummyProxy())

        assert mapping.getContainerKey() == "key"

    def test_clean(self):
        proxy = DummyProxy()
        proxy._set("key", "myvalue")
        mapping = self._makeOne("key", proxy)

        assert "key" in proxy._cached
        mapping._clean()
        assert "key" not in proxy._cached

        # Cleaning again won't throw errors
        assert mapping._clean() is None

    def test_abort(self):
        proxy = DummyProxy()
        proxy._set("key", "myvalue")
        mapping = self._makeOne("key", proxy)

        assert "key" in proxy._cached
        mapping.abort(None)
        assert "key" not in proxy._cached

    def test_savepoint(self):
        from Products.mcdutils.mapping import MemCacheMappingSavepoint

        mapping = self._makeOne("key", DummyProxy())

        sp = mapping.savepoint()
        assert isinstance(sp, MemCacheMappingSavepoint)

    def test_sortKey(self):
        mapping = self._makeOne("key", DummyProxy())

        assert mapping.sortKey() == "MemCacheMapping: key"

    def test_repr(self):
        KEYS = ("__ac_password", "passwd", "password")
        proxy = DummyProxy()
        proxy._set("key", "myvalue")
        mapping = self._makeOne("key", proxy)

        for pw_key in KEYS:
            mapping[pw_key] = "thisisapw"
        mapping["normal"] = "normalvalue"

        mapping_repr = repr(mapping)
        assert "thisisapw" not in mapping_repr
        for pw_key in KEYS:
            assert f"'{pw_key}': '<password obscured>'" in mapping_repr
        assert "'normal': 'normalvalue'" in mapping_repr

    def test_invalidate(self):
        """Tests invalidate method"""
        proxy = DummyProxy()
        proxy._set("key", "myvalue")
        mapping = self._makeOne("key", proxy)

        assert "key" in proxy._cached
        mapping.invalidate()
        assert "key" not in proxy._cached

        # Cleaning again won't throw errors
        assert mapping.invalidate() is None


class DummyClient:
    def _get_server(self, key):
        return self, key


class DummyProxy:
    def __init__(self):
        self._cached = {}

    def _set(self, key, value):
        self._cached[key] = value

    def _clean(self, key):
        with contextlib.suppress(KeyError):
            del self._cached[key]

    def delete(self, key):
        with contextlib.suppress(KeyError):
            del self._cached[key]

    client = DummyClient()
