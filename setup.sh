#!/bin/bash

# exit on any error
set -e

ROOT="$(dirname "$(realpath $0)")"
cd "$ROOT"
pwd

# client setup
cd client
npm install

# server setup
cd ../server
conda env create --file environment.yml
npm install

echo
echo
echo "done!"
echo "run: conda activate autocorrectenv"
echo "cd into $ROOT/server/python and run: pip install ."
echo "After that, go back to $ROOT and run setup_application.sh :)"
