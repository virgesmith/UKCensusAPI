#!/bin/bash

version=1.1.6

# package
python3 setup.py sdist bdist_wheel
# upload
twine upload --repository-url https://test.pypi.org/legacy/ dist/ukcensusapi-$version*
#twine upload --repository-url https://upload.pypi.org/legacy/ dist/ukcensusapi-$version*
if [ "$?" -ne "0" ]; then
  echo "upload failed"
  exit 1
fi

# test package in tmp env
# segregrated env PYTHONPATH="" to be certain
virtualenv -p python3 --no-site-packages /tmp/env
source /tmp/env/bin/activate

# local wheel
#python3 -m pip install  ~/dev/UKCensusAPI/dist/ukcensusapi-$version-py3-none-any.whl
# test pypi
python3 -m pip install --index-url https://test.pypi.org/simple/ UKCensusAPI --user
# real pypi 
#python3 -m pip install UKCensusAPI

ukcensus-query

# clean up
deactivate
rm -rf /tmp/env
