""" Product:  mcdutils

Implement Zope sessions using memcached as the backing store.

$Id: __init__.py,v 1.6 2006/06/07 05:43:09 tseaver Exp $
"""

class MemCacheError(IOError):
    pass

def initialize(context):

    from Products.mcdutils.proxy import MemCacheProxy
    from Products.mcdutils.proxy import addMemCacheProxyForm
    from Products.mcdutils.proxy import addMemCacheProxy
    context.registerClass(MemCacheProxy,
                          constructors=(addMemCacheProxyForm,
                                        addMemCacheProxy),
                          icon='www/proxy.gif',
                         )

    from Products.mcdutils.sessiondata import MemCacheSessionDataContainer
    from Products.mcdutils.sessiondata \
        import addMemCacheSessionDataContainerForm
    from Products.mcdutils.sessiondata import addMemCacheSessionDataContainer
    context.registerClass(MemCacheSessionDataContainer,
                          constructors=(addMemCacheSessionDataContainerForm,
                                        addMemCacheSessionDataContainer),
                          icon='www/sdc.gif',
                         )

    from Products.mcdutils.zcache import MemCacheZCacheManager
    from Products.mcdutils.zcache \
        import addMemCacheZCacheManagerForm
    from Products.mcdutils.zcache import addMemCacheZCacheManager
    context.registerClass(MemCacheZCacheManager,
                          constructors=(addMemCacheZCacheManagerForm,
                                        addMemCacheZCacheManager),
                          icon='www/zcm.gif',
                         )
