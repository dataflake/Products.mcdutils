""" RAMCacheManager workalike using memcache

$Id: zcache.py,v 1.1 2006/06/07 05:43:09 tseaver Exp $
"""
from AccessControl.SecurityInfo import ClassSecurityInfo
from Globals import InitializeClass
from OFS.Cache import CacheManager
from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.interface import implementedBy
from zope.interface import implements

from Products.mcdutils.interfaces import IZCache
from Products.mcdutils.interfaces import IZCacheManager

def aggregateKey(ob,
                 view_name='',
                 request=None,
                 request_names=(),
                 local_keys=None,
                ):
    """ Return a key to be used when retrieving or inserting a cache entry.

    o 'ob' is the object for whom the key is desired.

    o 'view_name' must be a string.

    o 'request' must be a mapping.

    o 'request_names' must be a sorted list of keys to be included in the key
      from 'request'

    o 'local_keys' is a mapping or None.
    """
    path = '/'.join(ob.getPhysicalPath())
    request_index = []
    local_index = []
    if request is None:
        request = {}
    if local_keys is None:
        local_keys = {}

    for key in request_names:
        val = request.get(key, '')
        request_index.append('%s:%s' % (str(key), str(val)))

    for key, val in local_keys.items():
        local_index.append('%s:%s' % (str(key), str(val)))
    local_index.sort()

    return '|'.join((path,
                     str(view_name),
                     ','.join(request_index),
                     ','.join(local_index),
                    ))

class MemCacheZCache(object):
    """ Implement ISDC via a memcache proxy.
    """
    implements(IZCache)
    security = ClassSecurityInfo()
    security.declareObjectPrivate()

    def __init__(self, proxy, request_names):
        self.proxy = proxy
        self.request_names = request_names

    def ZCache_invalidate(self, ob):
        """ See IZCache.
        """
        path = '/'.join(ob.getPhysicalPath())
        proxy = self.proxy
        keys = proxy.get(path)
        if keys is None:
            return
        for key in keys:
            proxy.remove(key)
        proxy.remove(path)

    def ZCache_get(self,
                   ob,
                   view_name='',
                   keywords=None,
                   mtime_func=None,
                   default=None,
                  ):
        """ See IZCache.
        """
        key = self._getKey(ob, view_name, keywords)

        value = self.proxy.get(key)

        if value is None:
            return default

        return value

    def ZCache_set(self,
                   ob,
                   data,
                   view_name='',
                   keywords=None,
                   mtime_func=None,
                  ):
        """ See IZCache.
        """
        path = '/'.join(ob.getPhysicalPath())
        proxy = self.proxy
        key = self._getKey(ob, view_name, keywords)
        proxy.set(key, data)

        keys = proxy.get(path)
        if keys is None:
            keys = {}
        if key not in keys:
            keys[key] = 1
            proxy.set(path, keys)

    def _getKey(self, ob, view_name, keywords):
        rnames = self.request_names
        if rnames:
            request = getattr(ob, 'REQUEST', {})
        else:
            request = {}

        return aggregateKey(ob, view_name, request, rnames, keywords)

InitializeClass(MemCacheZCache)

class MemCacheZCacheManager(CacheManager, SimpleItem, PropertyManager):
    """ Implement ISDC via a memcache proxy.
    """
    implements(IZCacheManager
             + implementedBy(CacheManager)
             + implementedBy(SimpleItem)
             + implementedBy(PropertyManager)
              )
    security = ClassSecurityInfo()

    _v_proxy = None
    proxy_path = None
    request_names = ()

    #
    #   ZMI
    #
    meta_type = 'MemCache Cache Manager'
    _properties = (
        {'id': 'proxy_path', 'type': 'string', 'mode': 'w'},
        {'id': 'request_names', 'type': 'lines', 'mode': 'w'},
    )

    manage_options = (PropertyManager.manage_options
                    + CacheManager.manage_options
                    + SimpleItem.manage_options
                     )

    security.declarePrivate('_get_proxy')
    def _get_proxy(self):
        if self._v_proxy is None:
            if self.proxy_path is None:
                # import late to avoid cycle
                from Products.mcdutils import MemCacheError
                raise MemCacheError('No proxy defined')
            self._v_proxy = self.unrestrictedTraverse(self.proxy_path)
        return self._v_proxy

    def ZCacheManager_getCache(self):
        """ See IZCacheManager.
        """
        names = list(self.request_names)
        names.sort()
        return MemCacheZCache(self._get_proxy(), tuple(names))

InitializeClass(MemCacheZCacheManager)


def addMemCacheZCacheManager(dispatcher, id, REQUEST):
    """ Add a MCSDC to dispatcher.
    """
    zcm = MemCacheZCacheManager()
    zcm._setId(id)
    dispatcher._setObject(id, zcm)
    REQUEST['RESPONSE'].redirect('%s/manage_workspace'
                                    % dispatcher.absolute_url())

addMemCacheZCacheManagerForm = PageTemplateFile('www/add_mczcm.pt', globals())
