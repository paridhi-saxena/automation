#!/usr/bin/env bash

export PROJPATH=$(pwd)
echo ''
echo "project path is: "  $PROJPATH
echo ''

source $PROJPATH/.venv/bin/activate
echo "Using python: "
python --version

python $PROJPATH/course-importer-validator/src_automation/csv_reader.py

deactivate