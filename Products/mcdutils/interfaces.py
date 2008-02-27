""" mcdutils product interfaces

$Id: interfaces.py,v 1.6 2006/06/07 05:43:09 tseaver Exp $
"""
from transaction.interfaces import IDataManager
from zope.interface import Attribute
from zope.interface import Interface

class ISessionDataContainer(Interface):
    """ Document the implied interface expected by Zope2's SessionDataManager.
    """
    def has_key(key):
        """ Return True if the container has the key, else False.
        """

    def new_or_existing(key):
        """ Return a mapping for 'key', creating it if needed.

        o The returned object must be Acquisition-wrappable.
        """

    def get(key):
        """ Return a mapping for 'key'.

        o Return None of no mapping exists.

        o If not None, the returned object must be Acquisition-wrappable.
        """

class IMemCacheMapping(IDataManager):
    """ Combine Python's mapping protocol with transaction management.
    """

class IMemCacheProxy(Interface):
    """ Manage client connection to a pool of memcached servers.
    """
    servers = Attribute(u'servers', u"""List of servers

Each item is a <host>:<port> server address.""")

    client = Attribute(u'client', u"""memcache.Client instance"""
                      )
    client.setTaggedValue('read_only', True)

    def get(key):
        """ Return the value stored in the cache under 'key'.
        """

    def get_multi(keys):
        """ Return a mapping of values stored in the cache under 'keys'.
        """

    def set(key, value):
        """ Store value for 'key'.

        o Return a boolean to indicate success.
        """

    def add(key, value):
        """ Store value (a mapping) for 'key'.

        o Return a boolean to indicate success.

        o Like 'set', but stores value only if the key does not already exist.
        """

    def replace(key, value):
        """ Store value (a mapping) for 'key'.

        o Return a boolean to indicate success.

        o Like 'set', but stores value only if the key already exists.
        """

    def delete(key, time=0):
        """ Remove the value stored in the cache under 'key'.

        o 'time', if passed an integer time value (in seconds) during
          which the memcached server will block new writes to this key
          (perhaps useful in preventing race conditions).

        o Return a boolean to indicate success.
        """

class IMemCacheSessionDataContainer(ISessionDataContainer):
    """ memcache-specific SDC, using a proxy.
    """
    proxy_path = Attribute(u"""Path to proxy.

No session operations are possible if the path is invalid.""")


class IZCache(Interface):
    """ Interface describing API for OFS.Cache.Cache.
    """
    def ZCache_invalidate(ob):
        """ Remove any entries from the cache for 'ob'.
        """

    def ZCache_get(ob, view_name, keywords, mtime_func, default):
        """ Fetch a cache entry for 'ob'.

        o If an object provides different views that would benefit from
          caching, it will set 'view_name', which should be treated as
          part of the cache key.  It defaults to the empty string.
         
        o 'keywords', if passed, will be a mapping containing keys that
          distinguish this cache entry from others even though
          'ob' and 'view_name' are the same;  the value should thus be
          part of the key for the entry.  DTMLMethods use keywords
          derived from the DTML namespace.
         
        o When the Cache calls 'ob.ZCacheable_getModTime',
          it should pass 'mtime_func' as an argument.  It is provided to
          allow cacheable objects to provide their own computation
          of the object's modification time.
         
        o If no matching entry is found, return 'default'.
        """

    def ZCache_set(ob, data, view_name, keywords, mtime_func):
        """ Store a value in the cache for 'ob'.

        o 'data' is the value to be stored.

        o See ZCache_get() for description of the 'keywords', 'mtime_func',
          and 'default' parameters.
        """

class IZCacheManager(Interface):
    """ Interface describing API for OFS.Cache.CacheManager. 
    """
    def ZCacheManager_getCache():
        """ Return an object implementing IZCache.
        """
