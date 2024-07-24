#!/bin/bash

echo '# 1. Remove build and dist folder'
rm -rf ./build ./dist ./src/ibm_sso.egg-info

echo '# 2. Build package'
python setup.py sdist bdist_wheel 

echo '# 3. Deploy'
twine upload --repository testpypi dist/*

echo '# 4. Done ...'
