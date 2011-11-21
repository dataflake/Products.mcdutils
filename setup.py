from setuptools import setup, find_packages

readme = open('README.txt').read()
history = open('CHANGES.txt').read()
long_description = readme + '\n\n' + history

setup(name='Products.mcdutils',
      version='0.2b3',
      description='A Zope2 product which provides facilities for storing sessions in memcached.',
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Framework :: Zope2'],
      keywords='session memcache memcached Products',
      author='Tres Seaver',
      author_email='tseaver@palladion.com',
      maintainer='Christian Theune',
      maintainer_email='ct@gocept.com',
      url='https://bitbucket.org/ctheune/mcdutils',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools', 'Zope2'])
