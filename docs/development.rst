Development
===========

Bug tracker
-----------
For bug reports, suggestions or questions please use the
GitHub issue tracker at
https://github.com/dataflake/Products.mcdutils/issues.


Getting the source code
-----------------------
The source code is maintained on GitHub. To check out the main branch:

.. code-block:: console

  $ git clone https://github.com/dataflake/Products.mcdutils.git

You can also browse the code online at
https://github.com/dataflake/Products.mcdutils


Preparing the development sandbox
---------------------------------
This project uses a Makefile to automate development, quality assurance, testing, and deployment tasks for a Zope application.

Prerequisites
-------------

- Python 3.11 or higher
- ``make`` (available on most Unix-like systems)

Getting Started
---------------

Initial Setup
~~~~~~~~~~~~~

.. code-block:: bash

   # Set up virtual environment and install dependencies
   make install

Development
~~~~~~~~~~~

.. code-block:: bash

   # Start local Zope instance (localhost:8080)
   make start

   # Access Zope console for debugging
   make zconsole

Available Commands
------------------

Development
~~~~~~~~~~~

- ``make install`` - Installs Zope and all dependencies
- ``make start`` - Starts Zope instance on localhost:8080
- ``make zconsole`` - Starts Zope console for debugging

Code Quality
~~~~~~~~~~~~

- ``make check`` - Runs all quality checks
- ``make format`` - Automatically formats code
- ``make lint`` - Checks code style and standards
- ``make manifest`` - Verifies MANIFEST.in file

Testing
~~~~~~~

- ``make test`` - Runs test suite
- ``make test-coverage`` - Runs tests with coverage report

Documentation
~~~~~~~~~~~~~

- ``make docs`` - Generates HTML documentation
- ``make watch-docs`` - Generates documentation with auto-reload


Dependencies
~~~~~~~~~~~~

- ``make dependency-graph`` - Generates dependency graph (SVG)
- ``make dependency-circular`` - Checks for circular dependencies

Release
~~~~~~~

- ``make changelog`` - Shows changelog draft
- ``make release`` - Publishes new package version

Configuration
~~~~~~~~~~~~~

- ``make config`` - Creates Zope instance configuration
- ``make pre-commit`` - Installs pre-commit hooks

Cleanup
~~~~~~~

- ``make clean`` - Removes temporary files and builds

Configuration
-------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

- ``PYTHON`` - Defines Python interpreter (default: python3)

Project Structure
~~~~~~~~~~~~~~~~~

- ``.venv/`` - Python virtual environment
- ``instance/`` - Zope instance configuration
- ``src/`` - Project source code
- ``docs/`` - Documentation

Dependencies
------------

The project uses:

- **Zope** 5.13
- **uv** - Fast package manager
- **mxdev** - Dependency management
- **Ruff** - Linter and formatter
- **Pytest** - Testing framework
- **Sphinx** - Documentation generation

Testing
-------

.. code-block:: bash

   # Run basic tests
   make test

   # Run tests with coverage
   make test-coverage

Documentation
-------------

.. code-block:: bash

   # Generate documentation
   make docs

   # Develop documentation with auto-reload
   make watch-docs

Deployment and Release
----------------------

Release Process
~~~~~~~~~~~~~~~

1. Check changes:

   .. code-block:: bash

      make changelog

2. Execute release:

   .. code-block:: bash

      make release

Code Quality
------------

The project follows Plone standards for code quality:

.. code-block:: bash

   # Complete verification
   make check

   # Formatting only
   make format

   # Linting only
   make lint

Maintenance
-----------

Environment Cleanup
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   make clean

Removes:

- Python cache files
- Temporary builds
- Coverage reports
- Virtual environment
- Temporary dependency files

Development
-----------

Recommended Setup
~~~~~~~~~~~~~~~~~

1. Run ``make pre-commit`` to install pre-commit hooks
2. Use ``make check`` before committing
3. Run ``make test`` to verify functionality

Dependency Checks
~~~~~~~~~~~~~~~~~
- ``make dependency-graph`` - Visualizes project dependencies
- ``make dependency-circular`` - Detects circular dependencies

