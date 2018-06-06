"""
Common utility/helpers
"""
import os
from pathlib import Path

def _expand_home(path):
  """
  pathlib doesn't interpret ~/ as $HOME
  This doesnt deal with other user's homes e.g. ~another/dir is not changed
  """
  return Path(path.replace("~/", str(Path.home()) + "/"))

def init_cache_dir(dir):
  """
  Checks path exists and is a writable directory
  Create if it doesnt exist
  Throw PermissionError if not
  """
  dir = _expand_home(dir)

  if not os.path.exists(dir):
    os.makedirs(dir)
  
  if not os.path.isdir(dir):
    raise PermissionError(str(dir) + " is not a directory")

  if not os.access(dir, os.W_OK):
    raise PermissionError(str(dir) + " is not writable")

  return dir