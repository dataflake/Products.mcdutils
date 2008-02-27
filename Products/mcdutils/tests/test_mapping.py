""" Unit tests for Products.mcdutils.mapping

$Id: test_mapping.py,v 1.2 2006/05/31 20:57:16 tseaver Exp $
"""
import unittest

class MemCacheMappingTests(unittest.TestCase):

    def _getTargetClass(self):
        from Products.mcdutils.mapping import MemCacheMapping
        return MemCacheMapping

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_conforms_to_IDataManager(self):
        from zope.interface.verify import verifyClass
        from transaction.interfaces import IDataManager
        verifyClass(IDataManager, self._getTargetClass())

    def test___setitem___triggers_register(self):
        mapping = self._makeOne('key', DummyProxy())
        self.failIf(mapping._p_changed)
        self.failIf(mapping._p_joined)
        mapping['abc'] = 123
        self.failUnless(mapping._p_changed)
        self.failUnless(mapping._p_joined)

class DummyClient:
    def _get_server(self, key):
        return self, key

class DummyProxy:
    def _set(self, key, value):
        pass

    client = DummyClient()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MemCacheMappingTests))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
