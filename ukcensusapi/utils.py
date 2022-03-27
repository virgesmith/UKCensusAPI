"""
Common utility/helpers
"""
from typing import Optional
from pathlib import Path
import requests


def init_cache_dir(cache_dir: Optional[str]) -> Path:
  """
  Checks path exists and is a writable directory
  Create if it doesnt exist
  Throw PermissionError if not
  """
  DEFAULT_CACHE_DIR = "~/.cache/ukcensusapi"
  if not cache_dir:
    cache_dir = DEFAULT_CACHE_DIR

  directory = Path(cache_dir).expanduser()
  directory.mkdir(parents=True, exist_ok=True)
  return directory


def check_online(url, t=5):
  try:
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0'}
    r = requests.get(url, timeout=t, headers=headers)
    r.raise_for_status()
    return True
  except (requests.exceptions.RequestException) as error:
    return False
