Installation and development
============================

.. highlight:: console

Getting the source code
-----------------------
The source code is maintained in the Git repository.::

  $ git clone https://github.com/dataflake/Products.mcdutils.git

Setting up a development sandbox
--------------------------------
Once you've obtained a source checkout, you need to run the buildout::

  $ cd Products.mcdutils
  $ python2.7 bootstrap.py
  $ bin/buildout

The ``bootstrap.py`` step is only needed after the initial checkout because
it produces the script ``bin/buildout``.

The buildout will create the scripts that are used for code testing
and documentation building, described below.

Testing code, determining test coverage and linting
---------------------------------------------------
Once the buildout has run, the unit tests can be run as follows::

  $ bin/test

Code coverage and linting is done through the script at ``bin/tox``::

  $ bin/tox

Calling it without any arguments will run the unit tests, code coverage
report and linting. You can see the tests configured for it with the ``-l``
switch::

  $ bin/tox -l
  py27
  lint-py27
  coverage-report

``py27`` represents the unit tests, run under Python 2.7. You can run each
of these by themselves with the ``-e`` switch::

  $ bin/tox -e coverage-report

Coverage report output is as text to the terminal, and as HTML files under
``parts/coverage/``.

The result of linting checks are shown as text on the terminal as well as
HTML files under ``parts/flake8/``


Building the documentation
--------------------------
The Sphinx documentation is built by doing the following from the
directory containing setup.py::

  $ cd docs
  $ make html

The finished HTML files are under `docs/_build/html`.