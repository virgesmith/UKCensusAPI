from setuptools import setup

def readme():
  with open('README.md') as f:
    return f.read()

setup(name='ukcensusapi',
  version='0.1',
  description='UK census data query automation',
  url='https://github.com/virgesmith/UKCensusAPI',
  author='Andrew P Smith',
  author_email='a.p.smith@leeds.ac.uk',
  license='MIT',
  packages=['ukcensusapi'],
  zip_safe=False,
  test_suite='nose.collector',
  tests_require=['nose'],
  scripts=['bin/query']
)
