""" Unit tests for Products.mcdutils.proxy

$Id: test_proxy.py,v 1.7 2006/05/31 20:57:16 tseaver Exp $
"""
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

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MemCacheProxyTests))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
