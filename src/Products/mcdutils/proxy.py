""" mcdutils proxy

$Id: proxy.py,v 1.11 2006/06/07 05:42:57 tseaver Exp $
"""
import memcache
import UserDict

from zope.interface import implementedBy
from zope.interface import implements

from AccessControl.SecurityInfo import ClassSecurityInfo
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.mcdutils.interfaces import IMemCacheProxy
from Products.mcdutils.mapping import MemCacheMapping

class FauxClient(UserDict.UserDict):

    def _get_server(self, key):
        return self, key

    def set(self, key, value):
        self[key] = value

class MemCacheProxy(SimpleItem, PropertyManager):
    """ Implement ISDC via a a pool of memcache servers.
    """
    implements(IMemCacheProxy
             + implementedBy(SimpleItem)
             + implementedBy(PropertyManager)
             )
    security = ClassSecurityInfo()

    _v_cached = None
    _v_client = None

    security.declarePrivate('_get_cached')
    def _get_cached(self):
        if self._v_cached is None:
            self._v_cached = {}
        return self._v_cached

    _cached = property(_get_cached,)

    security.declarePrivate('_get_client')
    def _get_client(self):
        if self._v_client is not None:
            return self._v_client

        if self.servers:
            client = self._v_client = memcache.Client(self.servers)
        else:
            client = self._v_client = FauxClient()

        return client

    client = property(_get_client,)

    _servers = ()

    security.declarePrivate('_set_servers')
    def _set_servers(self, value):
        self._servers = value
        try:
            del self._v_client
        except AttributeError:
            pass
        try:
            del self._v_cache
        except AttributeError:
            pass

    servers = property(lambda self: self._servers, _set_servers)

    #
    #   ZMI
    #
    meta_type = 'MemCache Proxy'
    _properties = (
        {'id': 'servers', 'type': 'lines', 'mode': 'w'},
    )

    manage_options = (PropertyManager.manage_options
                    + SimpleItem.manage_options
                     )

    security.declarePrivate('get')
    def get(self, key):
        """ See IMemCacheProxy.
        """
        mapping = self._cached.get(key)

        if mapping is None:
            mapping = self._get_remote(key)

        if mapping is not None:
            # Force this mapping to clean up after the transaction.
            mapping.register(mapping)

        return mapping

    security.declarePrivate('get_multi')
    def get_multi(self, keys):
        """ See IMemCacheProxy.
        """
        return self._get_remote_multi(keys)

    security.declarePrivate('set')
    def set(self, key, value):
        """ See IMemCacheProxy.
        """
        rc = self.client.set(key, value)
        try:
            del self._cached[key]
        except KeyError:
            pass
        return rc

    security.declarePrivate('add')
    def add(self, key, value):
        """ Store value (a mapping) for 'key'.

        o Return a boolean to indicate success.

        o Like 'set', but stores value only if the key does not already exist.
        """
        rc = self.client.add(key, value)
        try:
            del self._cached[key]
        except KeyError:
            pass
        return rc

    security.declarePrivate('replace')
    def replace(self, key, value):
        """ Store value (a mapping) for 'key'.

        o Return a boolean to indicate success.

        o Like 'set', but stores value only if the key already exists.
        """
        rc = self.client.replace(key, value)
        try:
            del self._cached[key]
        except KeyError:
            pass
        return rc

    security.declarePrivate('delete')
    def delete(self, key, time=0):
        """ Remove the value stored in the cache under 'key'.

        o Return a boolean to indicate success.

        o 'time', if nonzero, will be tested in the cache to determine
          whether the item's 
        """
        rc = self.client.delete(key, time)
        try:
            del self._cached[key]
        except KeyError:
            pass
        return rc

    security.declarePrivate('create')
    def create(self, key):
        """ See IMemCacheProxy.
        """
        mapping = self._cached[key] = MemCacheMapping(key, self)
        return mapping

    #
    #   Helper methods
    #
    security.declarePrivate('_get_remote')
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

    security.declarePrivate('_get_remote_multi')
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
            result[k] = mapping

        return result

InitializeClass(MemCacheProxy)


def addMemCacheProxy(dispatcher, id, REQUEST):
    """ Add a MCP to dispatcher.
    """
    proxy = MemCacheProxy()
    proxy._setId(id)
    dispatcher._setObject(id, proxy)
    REQUEST['RESPONSE'].redirect('%s/manage_workspace'
                                    % dispatcher.absolute_url())

addMemCacheProxyForm = PageTemplateFile('www/add_mcp.pt', globals())
