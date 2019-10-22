"""
Common utility/helpers
"""
import os
from pathlib import Path
from urllib import request
from urllib.error import HTTPError
from urllib.error import URLError
from socket import timeout


def _expand_home(path):
    """
    pathlib doesn't interpret ~/ as $HOME
    This doesnt deal with other user's homes e.g. ~another/dir is not changed
    """
    return Path(path.replace("~/", str(Path.home()) + "/"))


def init_cache_dir(directory):
    """
  Checks path exists and is a writable directory
  Create if it doesnt exist
  Throw PermissionError if not
  """
    directory = _expand_home(directory)

    if not os.path.exists(str(directory)):
        os.makedirs(str(directory))

    if not os.path.isdir(str(directory)):
        raise PermissionError(str(directory) + " is not a directory")

    if not os.access(str(directory), os.W_OK):
        raise PermissionError(str(directory) + " is not writable")

    return directory


def check_online(url, t=5):
    try:
        request.urlopen(url, timeout=t)
        return True
    except (HTTPError, URLError, timeout) as error:
        return False
