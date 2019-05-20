#!/bin/bash

# requires:
#   - mypy
#   - pylint

fail () {
  echo "Failed CI at stage $1"
  exit 1
}

echo '--- COMPLAINER 9001 ---'
cd herbert

# check type annotations
python3 -m mypy herbert.py berts common --ignore-missing-imports --strict-optional --python-version 3.7 --namespace-packages || fail 'TYPE CHECKING'

python3 -m pylint herbert.py berts common --confidence=HIGH || fail 'LINTING'
