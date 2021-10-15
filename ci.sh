#!/bin/bash

# requires:
#   - mypy
#   - pylint

fail () {
  echo "Failed CI at stage $1"
  if [ -n "$FAIL_ON_FAIL" ]; then
    exit 1
  fi
}

echo '--- COMPLAINER 9001 ---'
cd herbert || { echo "Invalid Directory"; exit 1; }

files="*.py common"
bert_files='berts'

PYTHONPATH="$PYTHONPATH:." python3 berts/testbert.py

# check type annotations
echo 'CHECKING TYPE ANNOTATIONS'
python3 -m mypy $files $bert_files --ignore-missing-imports --strict-optional --python-version 3.7 --namespace-packages || fail 'TYPE CHECKING'

# echo 'LINTING (BASIC)'
# python3 -m pylint $files --rcfile .pylintrc || fail 'LINTING'
# python3 -m pylint $bert_files --rcfile .pylintrc --disable=missing-docstring || fail 'LINTING BERTS'

echo 'LINTING (IGNORABLE)'
python3 -m pylint $files --rcfile .pylintrc --confidence='HIGH,INFERENCE,INFERENCE_FAILURE,UNDEFINED' --exit-zero
python3 -m pylint $bert_files --disable=missing-docstring --rcfile .pylintrc --confidence='HIGH,INFERENCE,INFERENCE_FAILURE,UNDEFINED' --exit-zero

echo 'PEP8'
python3 -m pycodestyle . --max-line-length 140 --exclude 'ext' || fail 'PEP8'

echo 'TESTS'
python3 -m unittest test/*.py

