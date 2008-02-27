# Run this test from 'zopectl run'
# Requires that we are running a memcached on localhost, port 11211
import transaction
from Products.mcdutils.proxy import MemCacheProxy

proxy = MemCacheProxy(['localhost:11211'])

session = proxy.new_or_existing('foobar')
print session

session['abc'] = 123
print session

transaction.commit()

proxy2 = MemCacheProxy(['localhost:11211'])

print proxy2.get('foobar')
