.. contents::

The 'mcdutils' product supplies a replacement for the ZODB-based session data
container supplied by the 'Transience' product, shipped with the Zope core.
Rather than using a ZODB storage as the backing store for session data, as
'Transience' does, 'mcdutils' stores session data in a cluster of one or more
'memcached' servers.

This approach is a bit of a cheat, as it uses the daemons as primary stores,
rather than as caches for results of an expensive query.  Nevertheless, the
semantics are not a bad match for typical session usage.

Installation
============

Ensure that the 'Products.mcdutils' egg is available on your Python path, e.g.
by running 'easy_install Products.mcdutils' or including it in your buildout
configuration.

Configuration
=============

1. After installation, add an instance of the 'MemCache Proxy' type from
   the ZMI add list, typically in the root of your ZODB, and give it a
   memorable name, e.g., 'mcproxy'.

2. Configure the proxy using its "Properties" tab.  Set the 'servers'
   property to a list of servers, one per line, where each line is in
   the format, '<host>:<port'.  For instance, to use the 'memcached'
   running on the default port on your local machine, the value would be
   'localhost:11211'.

3. Add an instance of the 'MemCache Session Data Container' type, e.g.
   'mcsdc' in the root.

4. Configure that instance on its "Properties" tab to use the proxy
   you created above (e.g., '/mcproxy').

5. Finally, on the main tab of your 'session_data_manager' instance
   (typically also in the root), change the 'Transient Object Container Path'
   value to match the location of your new proxy, e.g. '/mcsdc'.

You can test the memcached configuration on its "Test" tab.  Enter one or more
lines describing key-value pairs, where the "key" for your session is
separated from the value by the first space character.  Note that the session
values are displayed below the form.

Attribution
===========

Thanks go to Tres Seaver for implementing this product back in 2006.


Resources
=========

- The main memcached site explains the memcached architecture, and contains
  information on administering and tuning a memcached cluster.

  o http://www.danga.com/memcached/

- The Python client bindings for memcached are maintained by
  Sean Reifschneider at Tummy.com:

  o http://www.python.org/pypi/memcached/1.2_tummy6

- 'tugela' is an alternate cache daemon implementation, which stores
  its mapping using a Berkeley b-tree on disk.  It conforms to the same
  wire protocol as 'memcached':

  o http://meta.wikimedia.org/wiki/Tugela_Cache

- This product's home page and bug tracker:

  o https://bitbucket.org/ctheune/mcdutils
