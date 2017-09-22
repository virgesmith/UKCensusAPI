#!/usr/bin/env python

from setuptools import setup

def readme():
  with open('README.md') as f:
    return f.read()

setup(name='ukcensusapi',
  version='0.1',
  description='UK census data query automation',
  long_description=readme(),
  url='https://github.com/virgesmith/UKCensusAPI',
  author='Andrew P Smith',
  author_email='a.p.smith@leeds.ac.uk',
  license='MIT',
  packages=['ukcensusapi'],
  install_requires=['numpy', 'pandas'],
  python_requires='>=3',
  zip_safe=False,
  test_suite='nose.collector',
  tests_require=['nose'],
  package_data = {
    # paths relative to the package directory
    'ukcensusapi': ['../README.md', '../data/laMapping.csv'],
  },
  include_package_data=True
)
