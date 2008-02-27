""" Unit tests for Products.mcdutils.zcache

$Id: test_zcache.py,v 1.1 2006/06/07 05:43:09 tseaver Exp $
"""
import unittest

class TestsOf_aggregateKey(unittest.TestCase):

    def test_defaults(self):
        from Products.mcdutils.zcache import aggregateKey
        key = aggregateKey(DummyOb())
        self.assertEqual(key, '%s|||' % _DUMMY_PATH_STR)

    def test_explicit_view_name(self):
        from Products.mcdutils.zcache import aggregateKey
        key = aggregateKey(DummyOb(), view_name='VIEW_NAME')
        self.assertEqual(key, '%s|VIEW_NAME||' % _DUMMY_PATH_STR)

    def test_explicit_request_names(self):
        from Products.mcdutils.zcache import aggregateKey
        key = aggregateKey(DummyOb(),
                           request={'aaa': 'AAA',
                                    'bbb': 'BBB',
                                    'ccc': 'CCC',
                                   },
                           request_names=['aaa', 'ccc'],
                          )
        self.assertEqual(key, '%s||aaa:AAA,ccc:CCC|' % _DUMMY_PATH_STR)

    def test_explicit_local_keys(self):
        from Products.mcdutils.zcache import aggregateKey
        key = aggregateKey(DummyOb(), local_keys={'foo': 'bar', 'baz': 'bam'})
        self.assertEqual(key, '%s|||baz:bam,foo:bar' % _DUMMY_PATH_STR)

class MemCacheZCacheTests(unittest.TestCase):

    def _getTargetClass(self):
        from Products.mcdutils.zcache import MemCacheZCache
        return MemCacheZCache

    def _makeOne(self, proxy, request_names=(), *args, **kw):
        mczc = self._getTargetClass()(proxy, request_names, *args, **kw)
        return mczc

    def test_conforms_to_IZCache(self):
        from zope.interface.verify import verifyClass
        from Products.mcdutils.interfaces import IZCache

        verifyClass(IZCache, self._getTargetClass())

    def test_ZCache_get_cache_miss(self):
        proxy = DummyProxy()
        cache = self._makeOne(proxy)

        self.assertEqual(cache.ZCache_get(DummyOb()), None)

    def test_ZCache_get_cache_hit_default_args(self):
        proxy = DummyProxy()
        cache = self._makeOne(proxy)

        proxy._cached['%s|||' % _DUMMY_PATH_STR] = 'XYZZY'

        self.assertEqual(cache.ZCache_get(DummyOb()), 'XYZZY')

    def test_ZCache_get_cache_hit_view_name(self):
        proxy = DummyProxy()
        cache = self._makeOne(proxy)

        _cached = proxy._cached 
        proxy._cached['%s|||' % _DUMMY_PATH_STR] = 'XYZZY'
        proxy._cached['%s|foo||' % _DUMMY_PATH_STR] = 'ABCDEF'

        self.assertEqual(cache.ZCache_get(DummyOb(), view_name='foo'),
                         'ABCDEF')

    def test_ZCache_get_cache_miss_view_name(self):
        proxy = DummyProxy()
        cache = self._makeOne(proxy)

        _cached = proxy._cached 
        proxy._cached['%s|||' % _DUMMY_PATH_STR] = 'XYZZY'
        proxy._cached['%s|foo||' % _DUMMY_PATH_STR] = 'ABCDEF'

        self.assertEqual(cache.ZCache_get(DummyOb(), view_name='bar'), None)

    def test_ZCache_get_cache_hit_request_names(self):
        proxy = DummyProxy()
        cache = self._makeOne(proxy, request_names=('bar', 'qux'))

        _cached = proxy._cached 
        proxy._cached['%s|||' % _DUMMY_PATH_STR] = 'XYZZY'
        proxy._cached['%s||bar:baz,qux:|' % _DUMMY_PATH_STR] = 'ABCDEF'

        ob = DummyOb()
        ob.REQUEST = {'bar': 'baz', 'bam': 'bif'}

        self.assertEqual(cache.ZCache_get(ob), 'ABCDEF')

    def test_ZCache_invalidate(self):
        proxy = DummyProxy()
        cache = self._makeOne(proxy)

        _cached = proxy._cached 
        proxy._cached['%s|||' % _DUMMY_PATH_STR] = 'XYZZY'
        proxy._cached['%s|foo||' % _DUMMY_PATH_STR] = 'ABCDEF'
        proxy._cached['%s|bar||' % _DUMMY_PATH_STR] = 'LMNOP'

        keys = _cached.keys()
        _cached[_DUMMY_PATH_STR] = dict([(k, 1) for k in keys])

        cache.ZCache_invalidate(DummyOb())

        self.assertEqual(len(_cached), 0)

    def test_ZCache_set_simple(self):
        proxy = DummyProxy()
        cache = self._makeOne(proxy)

        _cached = proxy._cached 

        cache.ZCache_set(DummyOb(), 'XYZZY')

        self.assertEqual(len(_cached), 2)
        key = '%s|||' % _DUMMY_PATH_STR
        self.failUnless(key in _cached[_DUMMY_PATH_STR])
        self.assertEqual(_cached[key], 'XYZZY')

    def test_ZCache_set_with_view_name(self):
        proxy = DummyProxy()
        cache = self._makeOne(proxy)

        _cached = proxy._cached 

        cache.ZCache_set(DummyOb(), 'XYZZY', view_name='v')

        self.assertEqual(len(_cached), 2)
        key = '%s|v||' % _DUMMY_PATH_STR
        self.failUnless(key in _cached[_DUMMY_PATH_STR])
        self.assertEqual(_cached[key], 'XYZZY')

    def test_ZCache_set_replacing(self):
        proxy = DummyProxy()
        cache = self._makeOne(proxy)

        _cached = proxy._cached 
        key1 = '%s|||' % _DUMMY_PATH_STR
        key2 = '%s|v||' % _DUMMY_PATH_STR
        _cached[_DUMMY_PATH_STR] = {key1: 1, key2: 1}
        _cached[key1] = 'GHIJKL'
        _cached[key2] = 'ABCDE'

        cache.ZCache_set(DummyOb(), 'XYZZY', view_name='v')

        self.assertEqual(len(_cached), 3)

        self.failUnless(key1 in _cached[_DUMMY_PATH_STR])
        self.assertEqual(_cached[key1], 'GHIJKL')

        self.failUnless(key2 in _cached[_DUMMY_PATH_STR])
        self.assertEqual(_cached[key2], 'XYZZY')

class MemCacheZCacheManagerTests(unittest.TestCase):

    def _getTargetClass(self):
        from Products.mcdutils.zcache import MemCacheZCacheManager
        return MemCacheZCacheManager

    def _makeOne(self, *args, **kw):
        mczc = self._getTargetClass()(*args, **kw)
        return mczc

    def test_conforms_to_IZCacheManager(self):
        from zope.interface.verify import verifyClass
        from Products.mcdutils.interfaces import IZCacheManager

        verifyClass(IZCacheManager, self._getTargetClass())

    def test_ZCacheManager_getCache_with_proxy(self):
        mgr = self._makeOne()
        mgr.dummy_proxy = DummyProxy()
        mgr.proxy_path = 'dummy_proxy'
        mgr.request_names = ('foo', 'bar')

        cache = mgr.ZCacheManager_getCache()

        self.assertEqual(cache.proxy, mgr.dummy_proxy)
        self.assertEqual(cache.request_names, ('bar', 'foo'))


_DUMMY_PATH = ('path', 'to', 'dummy')
_DUMMY_PATH_STR = '/'.join(_DUMMY_PATH)

class DummyOb:
    def getPhysicalPath(self):
        return _DUMMY_PATH

class DummyProxy:
    def __init__(self):
        self._cached = {}

    def set(self, key, value):
        self._cached[key] = value

    def _get(self, key, default=None):
        return self._cached.get(key, default)

    get = _get

    def remove(self, key):
        del self._cached[key]

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestsOf_aggregateKey))
    suite.addTest(unittest.makeSuite(MemCacheZCacheTests))
    suite.addTest(unittest.makeSuite(MemCacheZCacheManagerTests))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
