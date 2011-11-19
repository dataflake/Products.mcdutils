""" memcache-aware transactional mapping.

$Id: mapping.py,v 1.5 2006/06/29 21:13:36 tseaver Exp $
"""
from persistent.mapping import PersistentMapping
import transaction
from transaction.interfaces import IDataManager
from zope.interface import implementedBy
from zope.interface import implements

from AccessControl.SecurityInfo import ClassSecurityInfo
from Acquisition import Explicit
from Globals import InitializeClass

class MemCacheMapping(Explicit, PersistentMapping):
    """ memcache-based mapping which manages its own transactional semantics
    """
    implements(IDataManager + implementedBy(PersistentMapping))
    security = ClassSecurityInfo()

    def __init__(self, key, proxy):
        PersistentMapping.__init__(self)
        self._p_oid = hash(key)
        self._p_jar = self   # we are our own data manager
        self._p_key = key
        self._p_proxy = proxy
        self._p_joined = False

    security.setDefaultAccess('allow')
    security.declareObjectPublic()

    set = PersistentMapping.__setitem__
    __guarded_setitem__ = PersistentMapping.__setitem__
    __guarded_delitem__ = PersistentMapping.__delitem__
    delete = PersistentMapping.__delitem__

    def __getstate__(self):
        return self.data

    def __setstate__(self, value):
        self.data = {}
        self.data.update(value)

    def getContainerKey(self):
        """ Fake out (I)Transient API.
        """
        return self._p_key

    def _clean(self):
        # Remove from proxy cache to force an update
        # from memcached during next access.
        try:
            del self._p_proxy._cached[self._p_key]
        except KeyError:
            pass

    security.declarePrivate('abort')
    def abort(self, txn):
        """ See IDataManager.
        """
        self._clean()

    security.declarePrivate('tpc_begin')
    def tpc_begin(self, txn):
        """ See IDataManager.
        """

    security.declarePrivate('commit')
    def commit(self, txn):
        """ See IDataManager.
        """

    security.declarePrivate('tpc_vote')
    def tpc_vote(self, txn):
        """ See IDataManager.
        """
        server, key = self._p_proxy.client._get_server(self._p_key)
        if server is None:
            from Products.mcdutils import MemCacheError
            raise MemCacheError("Can't reach memcache server!")

    security.declarePrivate('tpc_finish')
    def tpc_finish(self, txn):
        """ See IDataManager.
        """
        if self._p_changed:
            self._p_proxy.set(self._p_key, self) # no error handling
        self._p_changed = 0
        self._p_joined = False
        self._clean()

    security.declarePrivate('tpc_abort')
    def tpc_abort(self, txn):
        """ See IDataManager.
        """
        self._p_joined = False
        self._p_changed = 0
        self._clean()

    security.declarePrivate('sortKey')
    def sortKey(self):
        """ See IDataManager.
        """
        return 'MemCacheMapping: %s' % self._p_key

    security.declarePrivate('register')
    def register(self, obj):
        """ See IPersistentDataManager
        """
        if obj is not self:
            raise ValueError, "Can't be the jar for another object."

        if not self._p_joined:
            transaction.get().join(self)
            self._p_joined = True

InitializeClass(MemCacheMapping)
