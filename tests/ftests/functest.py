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
# Run this test from 'zopectl run'
# Requires that we are running a memcached on localhost, port 11211
from Products.mcdutils.proxy import MemCacheProxy

import transaction


proxy = MemCacheProxy(["localhost:11211"])

session = proxy.new_or_existing("foobar")
print(session)

session["abc"] = 123
print(session)

transaction.commit()

proxy2 = MemCacheProxy(["localhost:11211"])

print(proxy2.get("foobar"))
