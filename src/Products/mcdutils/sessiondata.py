""" Products.mcdutils session data container """
from AccessControl.class_init import InitializeClass
from AccessControl.SecurityInfo import ClassSecurityInfo
from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.interface import implementedBy
from zope.interface import implementer

from .interfaces import IMemCacheSessionDataContainer
from .mapping import MemCacheMapping


@implementer(IMemCacheSessionDataContainer + implementedBy(SimpleItem)
             + implementedBy(PropertyManager))
class MemCacheSessionDataContainer(SimpleItem, PropertyManager):
    """ Implement ISDC via a memcache proxy.
    """
    security = ClassSecurityInfo()

    _v_proxy = None
    proxy_path = ''
    zmi_icon = 'far fa-clock'

    def __init__(self, id, title=''):
        self.id = id
        self.title = title

    def _get_proxy(self):
        if self._v_proxy is None:
            if not self.proxy_path:
                from Products.mcdutils import MemCacheError
                raise MemCacheError('No proxy defined')
            self._v_proxy = self.unrestrictedTraverse(self.proxy_path)
        return self._v_proxy

    # proxy = property(_get_proxy,)  # can't acquire inside property!

    #
    #   ZMI
    #
    meta_type = 'MemCache Session Data Container'
    _properties = (
        {'id': 'proxy_path', 'type': 'string', 'mode': 'w'},
    )

    manage_options = (
        PropertyManager.manage_options
        + ({'action': 'addItemsToSessionForm', 'label': 'Test'},)
        + SimpleItem.manage_options)

    security.declarePublic('addItemsToSessionForm')  # NOQA: flake8: D001
    addItemsToSessionForm = PageTemplateFile('www/add_items.pt', globals())

    security.declarePublic('addItemsToSession')  # NOQA: flake8: D001

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
    security.declarePrivate('has_key')  # NOQA: flake8: D001

    def has_key(self, key):
        """ See ISessionDataContainer.
        """
        return self._get_proxy().get(key) is not None

    security.declarePrivate('new_or_existing')  # NOQA: flake8: D001

    def new_or_existing(self, key):
        """ See ISessionDataContainer.
        """
        mapping = self.get(key)

        if mapping is None:
            proxy = self._get_proxy()
            mapping = MemCacheMapping(key, proxy)
            proxy._cached[key] = mapping

        return mapping

    security.declarePrivate('get')  # NOQA: flake8: D001

    def get(self, key):
        """ See ISessionDataContainer.
        """
        return self._get_proxy().get(key)


InitializeClass(MemCacheSessionDataContainer)


def addMemCacheSessionDataContainer(dispatcher, id, title='', REQUEST=None):
    """ Add a MCSDC to dispatcher.
    """
    dispatcher._setObject(id, MemCacheSessionDataContainer(id, title=title))

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect('%s/manage_workspace'
                                     % dispatcher.absolute_url())


addMemCacheSessionDataContainerForm = PageTemplateFile('www/add_mcsdc.pt',
                                                       globals())
