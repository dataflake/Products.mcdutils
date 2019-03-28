""" Unit tests for Products.mcdutils.sessiondata """
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

    def _makeOne(self, id, title='', with_proxy=True):
        sdc = self._getTargetClass()(id, title=title)
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
        sdc = self._makeOne('mcsdc')
        self.assertFalse(sdc.has_key('foobar'))  # NOQA: flake8: W601
        self.assertIsNone(sdc.get('foobar'))

    def test_invalid_proxy_raises_MemCacheError(self):
        from Products.mcdutils import MemCacheError
        sdc = self._makeOne('mcsdc', with_proxy=False)
        self.assertRaises(MemCacheError,
                          sdc.has_key, 'foobar')  # NOQA: flake8: W601
        self.assertRaises(MemCacheError, sdc.get, 'foobar')
        self.assertRaises(MemCacheError, sdc.new_or_existing, 'foobar')

    def test_new_or_existing_returns_txn_aware_mapping(self):
        from persistent.mapping import PersistentMapping
        from transaction.interfaces import IDataManager
        sdc = self._makeOne('mcsdc')
        created = sdc.new_or_existing('foobar')
        self.assertTrue(isinstance(created, PersistentMapping))
        jar = created._p_jar
        self.assertFalse(jar is None)
        self.assertTrue(IDataManager.providedBy(jar))

    def test_has_key_after_new_or_existing_returns_True(self):
        sdc = self._makeOne('mcsdc')
        sdc.new_or_existing('foobar')
        self.assertTrue(sdc.has_key('foobar'))  # NOQA: flake8: W601

    def test_get_after_new_or_existing_returns_same(self):
        sdc = self._makeOne('mcsdc')
        created = sdc.new_or_existing('foobar')
        self.assertTrue(sdc.get('foobar') is created)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MemCacheSessionDataTests))
    return suite
