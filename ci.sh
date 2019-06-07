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
cd herbert

files='herbert.py berts common'

# check type annotations
echo 'CHECKING TYPE ANNOTATIONS'
python3 -m mypy $files --ignore-missing-imports --strict-optional --python-version 3.7 --namespace-packages || fail 'TYPE CHECKING'

echo 'LINTING (BASIC)'
python3 -m pylint $files --rcfile ../.pylintrc --confidence=HIGH,INFERENCE,INFERENCE_FAILURE || fail 'LINTING'

echo 'LINTING (IGNORABLE)'
python3 -m pylint $files --rcfile ../.pylintrc --confidence=UNDEFINED --exit-zero



