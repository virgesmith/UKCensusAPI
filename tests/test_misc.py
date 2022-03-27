
import pytest

from ukcensusapi import nomisweb, nrscotland, nisra


def test_cache_dir_invalid():
  with pytest.raises((OSError, PermissionError)):
    nomisweb.Nomisweb(cache_dir="/home/invalid")
  with pytest.raises((OSError, PermissionError)):
    nrscotland.NRScotland(cache_dir="/bin")
  with pytest.raises((OSError, PermissionError)):
    nisra.NISRA(cache_dir="/bin/ls")

