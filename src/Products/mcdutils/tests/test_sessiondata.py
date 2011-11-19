""" Unit tests for Products.mcdutils.proxy

$Id: test_sessiondata.py,v 1.5 2006/10/05 21:04:25 tseaver Exp $
"""
import unittest

class DummyClient:
    def _get_server(self, key):
        return self, key

class DummyProxy:
    def __init__(self):
        self._cached = {}

    def set(self, key, value):
        pass

    def _get(self, key, default=None):
        return self._cached.get(key, default)

    get = _get

class MemCacheSessionDataTests(unittest.TestCase):

    def _getTargetClass(self):
        from Products.mcdutils.sessiondata \
            import MemCacheSessionDataContainer
        return MemCacheSessionDataContainer

    def _makeOne(self, with_proxy=True, *args, **kw):
        sdc = self._getTargetClass()(*args, **kw)
        if with_proxy:
            sdc.dummy_proxy = DummyProxy()
            sdc.proxy_path = 'dummy_proxy'
        return sdc

    def test_conforms_to_ISessionDataContainer(self):
        from zope.interface.verify import verifyClass
        from Products.mcdutils.interfaces import ISessionDataContainer
        verifyClass(ISessionDataContainer, self._getTargetClass())

    def test_conforms_to_IMemCacheSessionDataContainer(self):
        from zope.interface.verify import verifyClass
        from Products.mcdutils.interfaces import IMemCacheSessionDataContainer
        verifyClass(IMemCacheSessionDataContainer, self._getTargetClass())

    def test_empty(self):
        sdc = self._makeOne()
        self.assertEqual(sdc.has_key('foobar'), False)
        self.assertEqual(sdc.get('foobar'), None)

    def test_invalid_proxy_raises_MemCacheError(self):
        from Products.mcdutils import MemCacheError
        sdc = self._makeOne(with_proxy=False)
        self.assertRaises(MemCacheError, sdc.has_key, 'foobar')
        self.assertRaises(MemCacheError, sdc.get, 'foobar')
        self.assertRaises(MemCacheError, sdc.new_or_existing, 'foobar')

    def test_new_or_existing_returns_txn_aware_mapping(self):
        from persistent.mapping import PersistentMapping
        from transaction.interfaces import IDataManager
        sdc = self._makeOne()
        created = sdc.new_or_existing('foobar')
        self.failUnless(isinstance(created, PersistentMapping))
        jar = created._p_jar
        self.failIf(jar is None)
        self.failUnless(IDataManager.providedBy(jar))

    def test_has_key_after_new_or_existing_returns_True(self):
        from persistent.mapping import PersistentMapping
        sdc = self._makeOne()
        created = sdc.new_or_existing('foobar')
        self.assertEqual(sdc.has_key('foobar'), True)

    def test_get_after_new_or_existing_returns_same(self):
        sdc = self._makeOne()
        created = sdc.new_or_existing('foobar')
        self.failUnless(sdc.get('foobar') is created)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MemCacheSessionDataTests))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
