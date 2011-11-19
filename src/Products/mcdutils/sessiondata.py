""" mcdutils session data container

$Id: sessiondata.py,v 1.3 2006/06/06 22:54:05 tseaver Exp $
"""
from zope.interface import implementedBy
from zope.interface import implements

from AccessControl.SecurityInfo import ClassSecurityInfo
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.mcdutils.interfaces import IMemCacheSessionDataContainer
from Products.mcdutils.mapping import MemCacheMapping

class MemCacheSessionDataContainer(SimpleItem, PropertyManager):
    """ Implement ISDC via a memcache proxy.
    """
    implements(IMemCacheSessionDataContainer
             + implementedBy(SimpleItem)
             + implementedBy(PropertyManager)
              )
    security = ClassSecurityInfo()

    _v_proxy = None
    proxy_path = None

    security.declarePrivate('_get_proxy')
    def _get_proxy(self):
        if self._v_proxy is None:
            if self.proxy_path is None:
                from Products.mcdutils import MemCacheError
                raise MemCacheError('No proxy defined')
            self._v_proxy = self.unrestrictedTraverse(self.proxy_path)
        return self._v_proxy

    #proxy = property(_get_proxy,)  # XXX can't acquire inside property!

    #
    #   ZMI
    #
    meta_type = 'MemCache Session Data Container'
    _properties = (
        {'id': 'proxy_path', 'type': 'string', 'mode': 'w'},
    )

    manage_options = (PropertyManager.manage_options
                    + ({'action': 'addItemsToSessionForm', 'label': 'Test'},)
                    + SimpleItem.manage_options
                     )

    security.declarePublic('addItemsToSessionForm')
    addItemsToSessionForm = PageTemplateFile('www/add_items.pt', globals())

    security.declarePublic('addItemsToSession')
    def addItemsToSession(self):
        """ Add key value pairs from 'items' textarea to the session.
        """
        request = self.REQUEST
        items = request.form.get('items', ())
        session = request['SESSION']

        before = len(session)
        count = len(items)

        for line in items:
            k, v = line.split(' ', 1)
            k = k.strip()
            v = v.strip()
            session[k] = v

        after = len(session)

        return 'Before: %d;  after: %d; # items: %d' % (before, after, count)

    #
    #   ISessionDataContainer implementation
    #
    security.declarePrivate('has_key')
    def has_key(self, key):
        """ See ISessionDataContainer.
        """
        return self._get_proxy().get(key) is not None

    security.declarePrivate('new_or_existing')
    def new_or_existing(self, key):
        """ See ISessionDataContainer.
        """
        mapping = self.get(key)

        if mapping is None:
            proxy = self._get_proxy()
            mapping = MemCacheMapping(key, proxy)
            proxy._cached[key] = mapping # XXX

        return mapping

    security.declarePrivate('get')
    def get(self, key):
        """ See ISessionDataContainer.
        """
        return self._get_proxy().get(key)

InitializeClass(MemCacheSessionDataContainer)


def addMemCacheSessionDataContainer(dispatcher, id, REQUEST):
    """ Add a MCSDC to dispatcher.
    """
    sdc = MemCacheSessionDataContainer()
    sdc._setId(id)
    dispatcher._setObject(id, sdc)
    REQUEST['RESPONSE'].redirect('%s/manage_workspace'
                                    % dispatcher.absolute_url())

addMemCacheSessionDataContainerForm = PageTemplateFile('www/add_mcsdc.pt',
                                                       globals())
