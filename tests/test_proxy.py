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

KEY = b"key1"


class TestFauxClient:
    def _getTargetClass(self):
        from Products.mcdutils.proxy import FauxClient

        return FauxClient

    def _makeOne(self):
        return self._getTargetClass()()

    def test_faux_client(self):
        # Faux client only fakes out a few methods
        fc = self._makeOne()

        assert fc._get_server(KEY) == (fc, KEY)
        fc.set(KEY, "value1")
        assert fc._get_server(KEY) == (fc, KEY)


class TestMemCacheProxy:
    def _getTargetClass(self):
        from Products.mcdutils.proxy import MemCacheProxy

        return MemCacheProxy

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def _makeOneWithMemcache(self, *args, **kw):
        from .helpers import DummyMemcache

        proxy = self._getTargetClass()(*args, **kw)
        proxy._v_client = DummyMemcache()
        return proxy

    def test_conforms_to_IMemCacheProxy(self):
        from Products.mcdutils.interfaces import IMemCacheProxy
        from zope.interface.verify import verifyClass

        verifyClass(IMemCacheProxy, self._getTargetClass())

    def test__init__(self):
        proxy = self._makeOne("proxy", title="Proxy")

        assert proxy.getId() == "proxy"
        assert proxy.servers == ()
        assert proxy.getProperty("servers") == ()
        assert proxy.title == "Proxy"
        assert proxy.getProperty("title") == "Proxy"

    def test__cached(self):
        proxy = self._makeOne("proxy")

        assert proxy._cached == {}

        proxy._v_cached = {"foo": "bar"}
        assert proxy._cached == {"foo": "bar"}

    def test_client(self):
        from memcache import Client

        proxy = self._makeOne("proxy")

        assert proxy.client is not None

        proxy._v_client = "x"
        assert proxy.client == "x"

        # Set a server, which should create a real client instance
        proxy.servers = ("127.0.0.1:9999",)
        assert isinstance(proxy.client, Client)

    def test__servers(self):
        proxy = self._makeOne("proxy")

        assert proxy.servers == ()
        proxy.servers = ("srv",)
        assert proxy.servers == ("srv",)

        # make sure all caches are cleared
        proxy._v_client = "client"
        proxy._v_cache = "cache"
        assert proxy._v_client is not None
        assert proxy._v_cache is not None
        proxy.servers = ("srv",)
        assert getattr(proxy, "_v_client", None) is None
        assert getattr(proxy, "_v_cache", None) is None

    def test_create(self):
        from Products.mcdutils.mapping import MemCacheMapping

        proxy = self._makeOne("proxy")

        created = proxy.create(KEY)
        assert isinstance(created, MemCacheMapping)

    def test_get_set(self):
        proxy = self._makeOneWithMemcache("proxy")

        assert proxy.get(KEY) is None
        assert proxy.set(KEY, proxy.create(KEY))
        assert proxy.get(KEY) == {}

        # This should also work when setting values that are
        # not MemCacheMapping instances
        KEY2 = b"key2"
        assert proxy.get(KEY2) is None
        assert proxy.set(KEY2, {"foo": "bar"})
        assert proxy.get(KEY2) == {"foo": "bar"}

    def test_get_multi(self):
        proxy = self._makeOneWithMemcache("proxy")

        assert proxy.get_multi([KEY, b"key2"]) == {KEY: None, b"key2": None}

    def test_add(self):
        proxy = self._makeOneWithMemcache("proxy")

        assert proxy.add(KEY, proxy.create(KEY))
        assert proxy.get(KEY) == {}

    def test_replace(self):
        proxy = self._makeOneWithMemcache("proxy")

        assert proxy.replace(KEY, proxy.create(KEY)) is None
        assert proxy.get(KEY) is None

        assert proxy.set(KEY, proxy.create(KEY))
        assert proxy.get(KEY) == {}

    def test_delete(self):
        proxy = self._makeOneWithMemcache("proxy")

        assert proxy.delete(KEY) is None
        assert proxy.create(KEY) == {}

        assert proxy.set(KEY, proxy.create(KEY))
        assert proxy.delete(KEY)
        assert proxy.get(KEY) is None
