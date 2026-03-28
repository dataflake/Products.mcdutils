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
""" memcache-aware transactional mapping """
import transaction
from AccessControl.class_init import InitializeClass
from AccessControl.SecurityInfo import ClassSecurityInfo
from persistent.mapping import PersistentMapping
from transaction.interfaces import IDataManagerSavepoint
from transaction.interfaces import ISavepointDataManager
from zope.interface import implementedBy
from zope.interface import implementer


@implementer(ISavepointDataManager + implementedBy(PersistentMapping))
class MemCacheMapping(PersistentMapping):
    """ memcache-based mapping which manages its own transactional semantics
    """
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

    def __of__(self, other):
        # Behavior change from prior versions due to issues in Python 3:
        # This class used to subclass from Acquisition.Explicit as well,
        # but under Python 3 that causes metaclass conflicts since
        # PersistentMapping's metaclass is abc.ABCMeta and
        # Acquisition.Explicit has ExtensionClass as metaclass.
        # Nasty workaround: Stub out ``__of__`` as the session data manager
        # still expects us to support ``__of__``, but this object does
        # _not_ support Acquisition anymore.
        return self

    def __getstate__(self):
        return self.data

    def __setstate__(self, value):
        self.data = {}
        self.data.update(value)

    def __repr__(self):
        # Overriding here to try and hide some password fields, like
        # the ZPublisher HTTPRequest class tries to do.
        new_dict = dict(self.data)
        for key in list(new_dict.keys()):
            k_str = (
                key.decode("utf-8", "replace")
                if isinstance(key, (bytes, bytearray))
                else str(key)
            )
            lower_key = k_str.lower()
            if any(
                marker in lower_key for marker in (
                    'passw',
                    'pwd',
                    'secret',
                    'token',
                    'cred')):
                new_dict[key] = '<password obscured>'
        return repr(new_dict)

    def has_key(self, key):
        """ Backwards compatibility under Python 3 """
        return key in self.data

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

    security.declarePrivate('abort')  # NOQA: D001

    def abort(self, txn):
        """ See IDataManager.
        """
        self._clean()

    security.declarePrivate('tpc_begin')  # NOQA: D001

    def tpc_begin(self, txn):
        """ See IDataManager.
        """

    security.declarePrivate('commit')  # NOQA: D001

    def commit(self, txn):
        """ See IDataManager.
        """

    security.declarePrivate('invalidate')  # NOQA: D001

    def invalidate(self):
        """ See TransientObject.
        """
        try:
            self._p_proxy.delete(self._p_key)
        except KeyError:
            pass

    security.declarePrivate('tpc_vote')  # NOQA: D001

    def tpc_vote(self, txn):
        """ See IDataManager.
        """
        server, key = self._p_proxy.client._get_server(self._p_key)
        if server is None:
            from Products.mcdutils import MemCacheError
            raise MemCacheError("Can't reach memcache server!")

    security.declarePrivate('tpc_finish')  # NOQA: D001

    def tpc_finish(self, txn):
        """ See IDataManager.
        """
        if self._p_changed:
            self._p_proxy.set(self._p_key, self)  # no error handling
        self._p_changed = 0
        self._p_joined = False
        self._clean()

    security.declarePrivate('tpc_abort')  # NOQA: D001

    def tpc_abort(self, txn):
        """ See IDataManager.
        """
        self._p_joined = False
        self._p_changed = 0
        self._clean()

    security.declarePrivate('sortKey')  # NOQA: D001

    def sortKey(self):
        """ See IDataManager.
        """
        return 'MemCacheMapping: %s' % self._p_key

    security.declarePrivate('register')  # NOQA: D001

    def register(self, obj):
        """ See IPersistentDataManager
        """
        if obj is not self:
            raise ValueError("Can't be the jar for another object.")

        if not self._p_joined:
            transaction.get().join(self)
            self._p_joined = True

    security.declarePrivate('savepoint')  # NOQA: D001

    def savepoint(self):
        """ See ITransaction
        """
        return MemCacheMappingSavepoint()


InitializeClass(MemCacheMapping)


@implementer(IDataManagerSavepoint)
class MemCacheMappingSavepoint:
    """ A simple savepoint object
    """

    def rollback(self):
        """ Roll back a savepoint

        Memcache and the python-memcached library don't have the concept
        of a rollback, so there is nothing useful to do here.
        """
        pass
