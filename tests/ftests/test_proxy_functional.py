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
"""Functional tests for Products.mcdutils.proxy"""


class TestMemCacheSDCFunc:
    def _makeOne(self):
        from Products.mcdutils.proxy import MemCacheProxy
        from Products.mcdutils.sessiondata import MemCacheSessionDataContainer

        sdc = MemCacheSessionDataContainer("mcsdc")
        sdc.mcproxy = MemCacheProxy("mcproxy")
        sdc.proxy_path = "mcproxy"

        return sdc

    def test_writing_to_mapping_no_memcache(self):
        from Products.mcdutils.mapping import MemCacheMapping

        sdc = self._makeOne()
        mapping = sdc.new_or_existing("foobar")
        assert isinstance(mapping, MemCacheMapping)
        assert not mapping._p_changed
        assert not mapping._p_joined
        mapping["abc"] = 1345
        assert mapping._p_changed
        assert mapping._p_joined
        import transaction

        transaction.commit()

    def test_writing_to_mapping_with_memcache(self):
        from Products.mcdutils.mapping import MemCacheMapping

        sdc = self._makeOne()
        sdc._get_proxy().servers = ("localhost:11211",)
        mapping = sdc.new_or_existing("foobar")
        assert isinstance(mapping, MemCacheMapping)
        assert not mapping._p_changed
        assert not mapping._p_joined
        mapping["abc"] = 1345
        assert mapping._p_changed
        assert mapping._p_joined
        import transaction

        transaction.commit()

    def test_writing_to_mapping_with_invalid_memcache_raises(self):
        from Products.mcdutils import MemCacheError

        sdc = self._makeOne()
        sdc._get_proxy().servers = ("nonesuch:999999",)
        mapping = sdc.new_or_existing("foobar")
        mapping["abc"] = 1345
        import pytest
        import transaction

        with pytest.raises(MemCacheError):
            transaction.commit()
        transaction.abort()
