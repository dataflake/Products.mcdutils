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
"""Products.mcdutils session data container"""

from __future__ import annotations

from .interfaces import IMemCacheSessionDataContainer
from .mapping import MemCacheMapping
from AccessControl.class_init import InitializeClass
from AccessControl.SecurityInfo import ClassSecurityInfo
from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.interface import implementedBy
from zope.interface import implementer
from ZPublisher.HTTPRequest import default_encoding


@implementer(
    IMemCacheSessionDataContainer
    + implementedBy(SimpleItem)
    + implementedBy(PropertyManager)
)
class MemCacheSessionDataContainer(SimpleItem, PropertyManager):
    """Implement ISDC via a memcache proxy."""

    security = ClassSecurityInfo()

    _v_proxy = None
    proxy_path = ""
    zmi_icon = "far fa-clock"

    def __init__(self, id_, title=""):
        self.id = id_
        self.title = title

    def _get_proxy(self):
        if self._v_proxy is None:
            if not self.proxy_path:
                from Products.mcdutils import MemCacheError

                raise MemCacheError("No proxy defined")
            self._v_proxy = self.unrestrictedTraverse(self.proxy_path)
        return self._v_proxy

    # proxy = property(_get_proxy,)  # can't acquire inside property!

    #
    #   ZMI
    #
    meta_type = "MemCache Session Data Container"
    _properties = ({"id": "proxy_path", "type": "string", "mode": "w"},)

    manage_options = (
        PropertyManager.manage_options  # noqa: RUF005
        + ({"action": "addItemsToSessionForm", "label": "Test"},)
        + SimpleItem.manage_options
    )

    security.declarePublic("addItemsToSessionForm")
    addItemsToSessionForm = PageTemplateFile("www/add_items.pt", globals())

    security.declarePublic("addItemsToSession")

    def addItemsToSession(self):
        """Add key value pairs from 'items' textarea to the session."""
        request = self.REQUEST
        items = request.form.get("items", ())
        session = request["SESSION"]

        before = len(session.keys())
        count = len(items)

        for line in items:
            if not isinstance(line, bytes):
                line = line.encode(default_encoding)
            k, v = line.split(b" ", 1)
            k = k.strip()
            v = v.strip()
            session[k] = v

        after = len(session.keys())

        return f"Before: {before};  after: {after}; # items: {count}"

    #
    #   ISessionDataContainer implementation
    #
    security.declarePrivate("has_key")

    def has_key(self, key):
        """See ISessionDataContainer."""
        return self._get_proxy().get(self._safe_key(key)) is not None

    security.declarePrivate("new_or_existing")

    def new_or_existing(self, key):
        """See ISessionDataContainer."""
        key = self._safe_key(key)
        mapping = self.get(key)

        if mapping is None:
            proxy = self._get_proxy()
            mapping = MemCacheMapping(key, proxy)
            proxy._cached[key] = mapping

        return mapping

    security.declarePrivate("get")

    def get(self, key):
        """See ISessionDataContainer."""
        return self._get_proxy().get(self._safe_key(key))

    def _safe_key(self, key):
        """Helper to ensure the key is always a binary string"""
        if isinstance(key, str):
            key = key.encode("UTF-8")
        return key


InitializeClass(MemCacheSessionDataContainer)


def addMemCacheSessionDataContainer(dispatcher, id, title="", REQUEST=None):  # noqa: A002
    """Add a MCSDC to dispatcher."""
    dispatcher._setObject(id, MemCacheSessionDataContainer(id, title=title))

    if REQUEST is not None:
        REQUEST["RESPONSE"].redirect(
            f"{dispatcher.absolute_url()}/manage_workspace"
        )


addMemCacheSessionDataContainerForm = PageTemplateFile(
    "www/add_mcsdc.pt", globals()
)
