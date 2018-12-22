#!/bin/bash

pushd "${VIRTUAL_ENV}" > /dev/null

python -m pylint --rcfile=pylintrc isim
python -m mypy --ignore-missing-imports isim/

python -m pylint --rcfile=pylintrc tests
python -m mypy --ignore-missing-imports tests/

popd > /dev/null

