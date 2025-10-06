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


class TestOf_aggregateKey:
    def test_defaults(self):
        from Products.mcdutils.zcache import aggregateKey

        key = aggregateKey(DummyOb())
        assert key == f"{_DUMMY_PATH_STR}|||"

    def test_explicit_view_name(self):
        from Products.mcdutils.zcache import aggregateKey

        key = aggregateKey(DummyOb(), view_name="VIEW_NAME")
        assert key == f"{_DUMMY_PATH_STR}|VIEW_NAME||"

    def test_explicit_request_names(self):
        from Products.mcdutils.zcache import aggregateKey

        key = aggregateKey(
            DummyOb(),
            request={"aaa": "AAA", "bbb": "BBB", "ccc": "CCC"},
            request_names=["aaa", "ccc"],
        )
        assert key == f"{_DUMMY_PATH_STR}||aaa:AAA,ccc:CCC|"

    def test_explicit_local_keys(self):
        from Products.mcdutils.zcache import aggregateKey

        key = aggregateKey(DummyOb(), local_keys={"foo": "bar", "baz": "bam"})
        assert key == f"{_DUMMY_PATH_STR}|||baz:bam,foo:bar"


class TestMemCacheZCache:
    def _getTargetClass(self):
        from Products.mcdutils.zcache import MemCacheZCache

        return MemCacheZCache

    def _makeOne(self, proxy, request_names=(), *args, **kw):
        mczc = self._getTargetClass()(proxy, request_names, *args, **kw)
        return mczc

    def test_conforms_to_IZCache(self):
        from Products.mcdutils.interfaces import IZCache
        from zope.interface.verify import verifyClass

        verifyClass(IZCache, self._getTargetClass())

    def test_ZCache_get_cache_miss(self):
        proxy = DummyProxy()
        cache = self._makeOne(proxy)

        assert cache.ZCache_get(DummyOb()) is None

    def test_ZCache_get_cache_hit_default_args(self):
        proxy = DummyProxy()
        cache = self._makeOne(proxy)

        proxy._cached[f"{_DUMMY_PATH_STR}|||"] = "XYZZY"

        assert cache.ZCache_get(DummyOb()) == "XYZZY"

    def test_ZCache_get_cache_hit_view_name(self):
        proxy = DummyProxy()
        cache = self._makeOne(proxy)

        proxy._cached[f"{_DUMMY_PATH_STR}|||"] = "XYZZY"
        proxy._cached[f"{_DUMMY_PATH_STR}|foo||"] = "ABCDEF"

        assert cache.ZCache_get(DummyOb(), view_name="foo") == "ABCDEF"

    def test_ZCache_get_cache_miss_view_name(self):
        proxy = DummyProxy()
        cache = self._makeOne(proxy)

        proxy._cached[f"{_DUMMY_PATH_STR}|||"] = "XYZZY"
        proxy._cached[f"{_DUMMY_PATH_STR}|foo||"] = "ABCDEF"

        assert cache.ZCache_get(DummyOb(), view_name="bar") is None

    def test_ZCache_get_cache_hit_request_names(self):
        proxy = DummyProxy()
        cache = self._makeOne(proxy, request_names=("bar", "qux"))

        proxy._cached[f"{_DUMMY_PATH_STR}|||"] = "XYZZY"
        proxy._cached[f"{_DUMMY_PATH_STR}||bar:baz,qux:|"] = "ABCDEF"

        ob = DummyOb()
        ob.REQUEST = {"bar": "baz", "bam": "bif"}

        assert cache.ZCache_get(ob) == "ABCDEF"

    def test_ZCache_invalidate(self):
        proxy = DummyProxy()
        cache = self._makeOne(proxy)

        _cached = proxy._cached
        proxy._cached[f"{_DUMMY_PATH_STR}|||"] = "XYZZY"
        proxy._cached[f"{_DUMMY_PATH_STR}|foo||"] = "ABCDEF"
        proxy._cached[f"{_DUMMY_PATH_STR}|bar||"] = "LMNOP"

        keys = _cached.keys()
        _cached[_DUMMY_PATH_STR] = dict.fromkeys(keys, 1)

        cache.ZCache_invalidate(DummyOb())

        assert len(_cached) == 0

    def test_ZCache_set_simple(self):
        proxy = DummyProxy()
        cache = self._makeOne(proxy)

        _cached = proxy._cached

        cache.ZCache_set(DummyOb(), "XYZZY")

        assert len(_cached) == 2
        key = f"{_DUMMY_PATH_STR}|||"
        assert key in _cached[_DUMMY_PATH_STR]
        assert _cached[key] == "XYZZY"

    def test_ZCache_set_with_view_name(self):
        proxy = DummyProxy()
        cache = self._makeOne(proxy)

        _cached = proxy._cached

        cache.ZCache_set(DummyOb(), "XYZZY", view_name="v")

        assert len(_cached) == 2
        key = f"{_DUMMY_PATH_STR}|v||"
        assert key in _cached[_DUMMY_PATH_STR]
        assert _cached[key] == "XYZZY"

    def test_ZCache_set_replacing(self):
        proxy = DummyProxy()
        cache = self._makeOne(proxy)

        _cached = proxy._cached
        key1 = f"{_DUMMY_PATH_STR}|||"
        key2 = f"{_DUMMY_PATH_STR}|v||"
        _cached[_DUMMY_PATH_STR] = {key1: 1, key2: 1}
        _cached[key1] = "GHIJKL"
        _cached[key2] = "ABCDE"

        cache.ZCache_set(DummyOb(), "XYZZY", view_name="v")

        assert len(_cached) == 3

        assert key1 in _cached[_DUMMY_PATH_STR]
        assert _cached[key1] == "GHIJKL"

        assert key2 in _cached[_DUMMY_PATH_STR]
        assert _cached[key2] == "XYZZY"


class TestMemCacheZCacheManager:
    def _getTargetClass(self):
        from Products.mcdutils.zcache import MemCacheZCacheManager

        return MemCacheZCacheManager

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_conforms_to_IZCacheManager(self):
        from Products.mcdutils.interfaces import IZCacheManager
        from zope.interface.verify import verifyClass

        verifyClass(IZCacheManager, self._getTargetClass())

    def test__init__(self):
        mgr = self._makeOne("zcache", title="ZCache Manager")

        assert mgr.getId() == "zcache"
        assert mgr.title == "ZCache Manager"
        assert mgr.getProperty("title") == "ZCache Manager"
        assert mgr.getProperty("proxy_path") == ""
        assert mgr.getProperty("request_names") == ()

    def test_ZCacheManager_getCache_with_proxy(self):
        mgr = self._makeOne("zcache")
        mgr.dummy_proxy = DummyProxy()
        mgr.proxy_path = "dummy_proxy"
        mgr.request_names = ("foo", "bar")

        cache = mgr.ZCacheManager_getCache()

        assert cache.proxy == mgr.dummy_proxy
        assert cache.request_names == ("bar", "foo")


_DUMMY_PATH = ("path", "to", "dummy")
_DUMMY_PATH_STR = "/".join(_DUMMY_PATH)


class DummyOb:
    def getPhysicalPath(self):
        return _DUMMY_PATH


class DummyProxy:
    def __init__(self):
        self._cached = {}

    def set(self, key, value):
        self._cached[key] = value

    def _get(self, key, default=None):
        return self._cached.get(key, default)

    get = _get

    def delete(self, key, time=0):
        try:
            del self._cached[key]
            return True
        except KeyError:
            return False
