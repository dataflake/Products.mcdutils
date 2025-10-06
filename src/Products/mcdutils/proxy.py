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
"""Memcache proxy"""

from __future__ import annotations

from .interfaces import IMemCacheProxy
from .mapping import MemCacheMapping
from AccessControl.class_init import InitializeClass
from AccessControl.SecurityInfo import ClassSecurityInfo
from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from typing import Any
from zope.interface import implementedBy
from zope.interface import implementer

import contextlib
import memcache


class FauxClient(dict):
    def _get_server(self, key):
        return self, key

    def set(self, key: str, value: Any):
        self[key] = value


@implementer(
    IMemCacheProxy + implementedBy(SimpleItem) + implementedBy(PropertyManager)
)
class MemCacheProxy(SimpleItem, PropertyManager):
    """Implement ISDC via a a pool of memcache servers."""

    security = ClassSecurityInfo()

    _v_cached = None
    _v_client = None
    zmi_icon = "fas fa-tachometer-alt"

    def __init__(self, id_, title=""):
        self.id = id_
        self.title = title

    def _get_cached(self):
        if self._v_cached is None:
            self._v_cached = {}
        return self._v_cached

    _cached = property(_get_cached)

    def _get_client(self):
        if self._v_client is not None:
            return self._v_client

        if self.servers:
            client = self._v_client = memcache.Client(self.servers)
        else:
            client = self._v_client = FauxClient()

        return client

    client = property(_get_client)

    _servers = ()

    def _set_servers(self, value):
        self._servers = value
        with contextlib.suppress(AttributeError):
            del self._v_client
        with contextlib.suppress(AttributeError):
            del self._v_cache

    servers = property(lambda self: self._servers, _set_servers)

    #
    #   ZMI
    #
    meta_type = "MemCache Proxy"
    _properties = (
        {"id": "title", "type": "string", "mode": "w"},
        {"id": "servers", "type": "ulines", "mode": "w"},
    )

    manage_options = PropertyManager.manage_options + SimpleItem.manage_options

    security.declarePrivate("get")

    def get(self, key):
        """See IMemCacheProxy."""
        mapping = self._cached.get(key)

        if mapping is None:
            mapping = self._get_remote(key)

        if isinstance(mapping, MemCacheMapping):
            # Force this mapping to clean up after the transaction.
            mapping.register(mapping)

        return mapping

    security.declarePrivate("get_multi")

    def get_multi(self, keys):
        """See IMemCacheProxy."""
        return self._get_remote_multi(keys)

    security.declarePrivate("set")

    def set(self, key: str, value: Any):
        """See IMemCacheProxy."""
        rc = self.client.set(key, value)
        with contextlib.suppress(KeyError):
            del self._cached[key]
        return rc

    security.declarePrivate("add")

    def add(self, key, value):
        """Store value (a mapping) for 'key'.

        o Return a boolean to indicate success.

        o Like 'set', but stores value only if the key does not already exist.
        """
        rc = self.client.add(key, value)
        with contextlib.suppress(KeyError):
            del self._cached[key]
        return rc

    security.declarePrivate("replace")

    def replace(self, key, value):
        """Store value (a mapping) for 'key'.

        o Return a boolean to indicate success.

        o Like 'set', but stores value only if the key already exists.
        """
        rc = self.client.replace(key, value)
        with contextlib.suppress(KeyError):
            del self._cached[key]
        return rc

    security.declarePrivate("delete")

    def delete(self, key, time=0):
        """Remove the value stored in the cache under 'key'.

        o Return a boolean to indicate success.

        o 'time', if nonzero, will be tested in the cache to determine
          whether the item's
        """
        rc = self.client.delete(key, time)
        with contextlib.suppress(KeyError):
            del self._cached[key]
        return rc

    security.declarePrivate("create")

    def create(self, key):
        """See IMemCacheProxy."""
        mapping = self._cached[key] = MemCacheMapping(key, self)
        return mapping

    #
    #   Helper methods
    #
    def _get_remote(self, key):
        mapping = self._cached[key] = self.client.get(key)
        if isinstance(mapping, MemCacheMapping):
            mapping._p_proxy = self
            mapping._p_key = key
            mapping._p_oid = hash(key)
            mapping._p_jar = mapping
            mapping._p_joined = False
            mapping._p_changed = 0
        return mapping

    def _get_remote_multi(self, keys):
        meta_map = self.client.get_multi(keys)
        result = {}
        for key, mapping in meta_map.items():
            if isinstance(mapping, MemCacheMapping):
                mapping._p_proxy = self
                mapping._p_key = key
                mapping._p_oid = hash(key)
                mapping._p_jar = mapping
                mapping._p_joined = False
                mapping._p_changed = 0
            result[key] = mapping

        return result


InitializeClass(MemCacheProxy)


def addMemCacheProxy(dispatcher, id, title="", REQUEST=None):  # noqa: A002
    """Add a MCP to dispatcher."""
    dispatcher._setObject(id, MemCacheProxy(id, title=title))

    if REQUEST is not None:
        REQUEST["RESPONSE"].redirect(
            f"{dispatcher.absolute_url()}/manage_workspace"
        )


addMemCacheProxyForm = PageTemplateFile("www/add_mcp.pt", globals())
