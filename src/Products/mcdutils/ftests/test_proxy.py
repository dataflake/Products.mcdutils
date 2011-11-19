""" Functional tests for Products.mcdutils.proxy

$Id: test_proxy.py,v 1.3 2006/05/31 20:57:16 tseaver Exp $
"""
import unittest

class MemCacheSDCFuncTests(unittest.TestCase):

    def _makeOne(self):
        from Products.mcdutils.sessiondata import MemCacheSessionDataContainer
        from Products.mcdutils.proxy import MemCacheProxy
        sdc = MemCacheSessionDataContainer()
        sdc.mcproxy = MemCacheProxy()
        sdc.proxy_path = 'mcproxy'

        return sdc

    def test_writing_to_mapping_no_memcache(self):
        from Products.mcdutils.mapping import MemCacheMapping

        sdc = self._makeOne()
        mapping = sdc.new_or_existing('foobar')
        self.failUnless(isinstance(mapping, MemCacheMapping))
        self.failIf(mapping._p_changed)
        self.failIf(mapping._p_joined)
        mapping['abc'] = 1345
        self.failUnless(mapping._p_changed)
        self.failUnless(mapping._p_joined)
        import transaction
        transaction.commit()

    def test_writing_to_mapping_with_memcache(self):
        from Products.mcdutils.mapping import MemCacheMapping

        sdc = self._makeOne()
        sdc._get_proxy().servers = ('localhost:11211',)
        mapping = sdc.new_or_existing('foobar')
        self.failUnless(isinstance(mapping, MemCacheMapping))
        self.failIf(mapping._p_changed)
        self.failIf(mapping._p_joined)
        mapping['abc'] = 1345
        self.failUnless(mapping._p_changed)
        self.failUnless(mapping._p_joined)
        import transaction
        transaction.commit()

    def test_writing_to_mapping_with_invalid_memcache_raises(self):
        from Products.mcdutils import MemCacheError

        sdc = self._makeOne()
        sdc._get_proxy().servers = ('nonesuch:999999',)
        mapping = sdc.new_or_existing('foobar')
        mapping['abc'] = 1345
        import transaction
        self.assertRaises(MemCacheError, transaction.commit)
        transaction.abort()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MemCacheSDCFuncTests))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
