from setuptools import find_packages
from setuptools import setup


readme = open('README.rst').read()
history = open('CHANGES.txt').read()
long_description = readme + '\n\n' + history

setup(name='Products.mcdutils',
      version='1.0',
      description=('A Zope2 product which provides facilities for'
                   'storing sessions in memcached.'),
      long_description=long_description,
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Zope',
        'Framework :: Zope2',
        'Framework :: Zope :: 2',
        'Framework :: Zope :: 4',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Session'],
      keywords='session memcache memcached Products',
      author='Tres Seaver and contributors',
      author_email='tseaver@palladion.com',
      maintainer='Jens Vagelpohl',
      maintainer_email='jens@netz.ooo',
      url='https://github.com/dataflake/Products.mcdutils',
      license='ZPL 2.1',
      packages=find_packages('src'),
      include_package_data=True,
      namespace_packages=['Products'],
      package_dir={'': 'src'},
      zip_safe=False,
      python_requires='>=2.7',
      install_requires=[
        'setuptools',
        'Zope2',
        ],
      extras_require={
        'docs': ['repoze.sphinx.autointerface', 'Sphinx'],
        },
      )
