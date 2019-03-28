""" Unit tests for Products.mcdutils.proxy """
import unittest


class MemCacheProxyTests(unittest.TestCase):

    def _getTargetClass(self):
        from Products.mcdutils.proxy import MemCacheProxy
        return MemCacheProxy

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_conforms_to_IMemCacheProxy(self):
        from zope.interface.verify import verifyClass
        from Products.mcdutils.interfaces import IMemCacheProxy
        verifyClass(IMemCacheProxy, self._getTargetClass())

    def test__cached(self):
        proxy = self._makeOne('proxy')

        self.assertEqual(proxy._cached, {})

        proxy._v_cached = {'foo': 'bar'}
        self.assertEqual(proxy._cached, {'foo': 'bar'})

    def test_client(self):
        proxy = self._makeOne('proxy')

        self.assertIsNotNone(proxy.client)

        proxy._v_client = 'x'
        self.assertEqual(proxy.client, 'x')

    def test__servers(self):
        proxy = self._makeOne('proxy')

        self.assertEqual(proxy.servers, ())
        proxy.servers = ('srv',)
        self.assertEqual(proxy.servers, ('srv',))

        # make sure all caches are cleared
        proxy._v_client = 'client'
        proxy._v_cache = 'cache'
        self.assertIsNotNone(getattr(proxy, '_v_client'))
        self.assertIsNotNone(getattr(proxy, '_v_cache'))
        proxy.servers = ('srv',)
        self.assertIsNone(getattr(proxy, '_v_client', None))
        self.assertIsNone(getattr(proxy, '_v_cache', None))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MemCacheProxyTests))
    return suite
