Change log
==========

5.0.0 (2025-10-06)
-------------------

- Added module ``reconnecting.py`` with client ``ReconnectingClient``:

  - Automatic reconnection on memcached network/server failures.
  - Optional *monkey-patch* replacing ``memcache.Client``.
  - Configuration via environment variables:

    - ``MCDUTILS_DISABLE_RECONNECT`` (disables).
    - ``MCDUTILS_BACKOFF_MIN_MS`` and ``MCDUTILS_BACKOFF_MAX_MS`` (*backoff* intervals).
    - ``MCDUTILS_LOG`` / ``MCDUTILS_LOG_LEVEL`` (structured logs).
    - ``MCDUTILS_METRICS`` (enables internal metrics).

  - Prometheus metrics export via function ``export_prometheus_textfile``.

- Implemented automatic *retry* in ``tpc_vote`` of ``MemCacheMapping``:

  - New function ``_tpc_vote_with_retry`` encapsulates ``MemCacheError`` failures.
  - Configuration via environment variables:

    - ``MCDUTILS_DISABLE_TPC_RETRY`` (disables retry).
    - ``MCDUTILS_TPC_RETRY_ATTEMPTS`` (number of extra attempts).
    - ``MCDUTILS_TPC_RETRY_BACKOFF_MS`` (time between attempts).

  - Additional metrics registration: ``tpc_retry_attempts_total``,
    ``tpc_retry_success_total``, ``tpc_retry_fail_total`` and accumulated *backoff* times.


4.2 (2023-12-28)
----------------

- Add support for Python 3.12.


4.1 (2023-10-03)
----------------

- Adds invalidate method to MemCacheMapping and test


4.0 (2023-02-02)
----------------

- Drop support for Python 2.7, 3.5, 3.6.


3.3 (2023-01-15)
----------------

- Add support for Python 3.10 and 3.11.


3.2 (2021-09-03)
----------------

- reorganized package to use current zopefoundation standards

- claim compatibility with Python 3.9 and Zope 5

- fixed type error on adding session items via ZMI test page


3.1 (2021-01-01)
----------------

- revised ZMI 'Test Adding Items to Session'


3.0 (2020-08-07)
----------------

- packaging cleanup and test fixing due to shifting dependencies

- drop Zope 2 compatibility claims and tests


2.5 (2019-11-13)
----------------

- implement transaction savepoint support
  (`#3 <https://github.com/dataflake/Products.mcdutils/issues/3>`_)


2.4 (2019-10-23)
----------------

- attempt to hide session values that may contain passwords in ``__repr__``
  which is used when rendering the ``REQUEST`` object as string.


2.3 (2019-10-13)
----------------

- rely on the Zope 4.x branch for Python 2 compatibility

- update description to replace Zope2 wording with just Zope

- reorganize source folder structure and drop the ``src`` folder


2.2 (2019-05-21)
----------------

- add an implementation for ``has_key`` which is gone under Python 3


2.1 (2019-03-31)
----------------

- fix wrong method call during cache manager record invalidation
  (`#1 <https://github.com/dataflake/Products.mcdutils/issues/1>`_)


2.0 (2019-03-28)
----------------

- make sure ``zcache.aggregateKey`` does not create unsuitable MemCache keys

- allow storing values that don't conform to ``IMemCacheMapping``

- add ability to set a title for a MemCacheZCacheManager

- Python 3 compatibility

- switch to the ``python-memcached`` library and remove the old ``memcache``
  library module inside this package, which is actually a really old version
  of ``python-memcached``.

Possible breaking change
~~~~~~~~~~~~~~~~~~~~~~~~

The objects returned by Zope's session data manager are implicitly expected
to support Acquisition. Zope's session data manager uses it to insert itself
into the object's acquisition chain. However, under Python 3 Acquisition can
no longer be supported by the session data objects due to a metaclass conflict
between the classes ``permisstence.mapping.PersistentMapping`` and
``Acquisition.Explicit``. This may break expectations for code consuming the
session data objects from this package.


1.0 (2019-03-28)
----------------

- Zope 4 compatibility

- documentation using Sphinx

- ``tox`` configuration for unit, coverage and code quality tests

- package configuration cleanup

- full ``flake8`` compliance

- add ability to set a title for a MemcacheProxy

- add ability to set a title for a MemcacheSessionDataContainer


0.2b3 (2011-11-21)
------------------

- Extend MANIFEST.in to include other missing files (.gif, .pt, .txt)


0.2b2 (2011-11-21)
------------------

- Fix source distribution by including README.txt and CHANGES.txt via
  manifest.

- Include test runner in buildout and fix broken tests.


0.2b1 (2011-11-19)
------------------

- Turn product into an egg and release on PyPI.

- Implement a forced refresh of the in-process cache of memcache data at the
  end of transactions to avoid stale data.

- mapping.py: Added 'getContainerKey' method to 'MemCacheMapping' in
  order to make it compatible with the API of the TemporaryFolder version
  (allows the session testing rig code can generate error messages).

- Added (preliminary) RAMCacheManager replacement.

- Removed  proxy's 'create' method, to allow other multiple of data to be
  stored.  The session data container now handles instantiating the
  mapping.

- Fixed the pickling of mappings *correctly*, instead of requiring that
  the proxy pick out the 'data' member.

- Expanded API for IProxy to expose more of the memcached client API.


0.1 (2006-05-31)
----------------

- CVS tag, 'mcdutils-0_1'

- Initial public release.