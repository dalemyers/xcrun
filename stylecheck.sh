#!/bin/bash

python -m black --line-length 100 isim tests
python -m pylint --rcfile=pylintrc isim tests
python -m mypy --ignore-missing-imports isim/ tests/

