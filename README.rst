.. image:: https://api.travis-ci.org/dataflake/Products.mcdutils.svg?branch=master
   :target: https://travis-ci.org/dataflake/Products.mcdutils

.. image:: https://readthedocs.org/projects/mcdutils/badge/?version=latest
   :target: https://mcdutils.readthedocs.io
   :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/Products.mcdutils.svg
   :target: https://pypi.python.org/pypi/Products.mcdutils
   :alt: PyPI

.. image:: https://img.shields.io/pypi/pyversions/Products.mcdutils.svg
   :target: https://pypi.python.org/pypi/Products.mcdutils
   :alt: Python versions

===================
 Products.mcdutils
===================
The `Products.mcdutils` product supplies a replacement for the ZODB-based
session data container supplied by the `Transience` product, shipped with
the Zope core prior to Zope 4 and available as a separate package after that.
Rather than using a ZODB storage as the backing store for session data, as
`Transience` does, `Products.mcdutils` stores session data in a cluster of
one or more `memcached` servers.

This approach is a bit of a cheat, as it uses the daemons as primary stores,
rather than as caches for results of an expensive query.  Nevertheless, the
semantics are not a bad match for typical session usage.


Documentation
=============
Documentation is available at
https://mcdutils.readthedocs.io/


Bug tracker
===========
A bug tracker is available at
https://github.com/dataflake/Products.mcdutils/issues

Attribution
===========
Thanks go to...

- Tres Seaver for implementing this product back in 2006
- Christian Theune for making it available as egg on PyPI in 2011
- Jens Vagelpohl for preparing it for Zope 4 and Python 3
