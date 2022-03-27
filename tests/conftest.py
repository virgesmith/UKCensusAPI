import pytest

from ukcensusapi import nomisweb, nrscotland, nisra


TEST_CACHE_DIR = "/tmp/ukcensusapi"

@pytest.fixture(scope='session')
def api_ew():
  return nomisweb.api_ew(cache_dir=TEST_CACHE_DIR, verbose=True)


@pytest.fixture(scope='session')
def api_sc():
  return nrscotland.api_sc(cache_dir=TEST_CACHE_DIR)


@pytest.fixture(scope='session')
def api_ni():
  return nisra.api_ni(cache_dir=TEST_CACHE_DIR)

