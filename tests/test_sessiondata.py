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


class DummyClient:
    def _get_server(self, key):
        return self, key


class DummyProxy:
    def __init__(self):
        self._cached = {}

    def set(self, key, value):
        pass

    def _get(self, key, default=None):
        return self._cached.get(key, default)

    get = _get


class TestMemCacheSessionData:
    def _getTargetClass(self):
        from Products.mcdutils.sessiondata import MemCacheSessionDataContainer

        return MemCacheSessionDataContainer

    def _makeOne(self, id_, title="", with_proxy=True):
        sdc = self._getTargetClass()(id_, title=title)
        if with_proxy:
            sdc.dummy_proxy = DummyProxy()
            sdc.proxy_path = "dummy_proxy"
        return sdc

    def test_conforms_to_ISessionDataContainer(self):
        from Products.mcdutils.interfaces import ISessionDataContainer
        from zope.interface.verify import verifyClass

        verifyClass(ISessionDataContainer, self._getTargetClass())

    def test_conforms_to_IMemCacheSessionDataContainer(self):
        from Products.mcdutils.interfaces import IMemCacheSessionDataContainer
        from zope.interface.verify import verifyClass

        verifyClass(IMemCacheSessionDataContainer, self._getTargetClass())

    def test_empty(self):
        sdc = self._makeOne("mcsdc")
        assert not sdc.has_key("foobar")
        assert sdc.get("foobar") is None

    def test_invalid_proxy_raises_MemCacheError(self):
        from Products.mcdutils import MemCacheError

        sdc = self._makeOne("mcsdc", with_proxy=False)
        import pytest

        with pytest.raises(MemCacheError):
            sdc.has_key("foobar")
        import pytest

        with pytest.raises(MemCacheError):
            sdc.get("foobar")
        import pytest

        with pytest.raises(MemCacheError):
            sdc.new_or_existing("foobar")

    def test_new_or_existing_returns_txn_aware_mapping(self):
        from persistent.mapping import PersistentMapping
        from transaction.interfaces import IDataManager

        sdc = self._makeOne("mcsdc")
        created = sdc.new_or_existing("foobar")
        assert isinstance(created, PersistentMapping)
        jar = created._p_jar
        assert jar is not None
        assert IDataManager.providedBy(jar)

    def test_has_key_after_new_or_existing_returns_True(self):
        sdc = self._makeOne("mcsdc")
        sdc.new_or_existing("foobar")
        assert sdc.has_key("foobar")

    def test_get_after_new_or_existing_returns_same(self):
        sdc = self._makeOne("mcsdc")
        created = sdc.new_or_existing("foobar")
        assert sdc.get("foobar") is created
