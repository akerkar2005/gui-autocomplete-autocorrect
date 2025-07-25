#!/bin/bash

# exit on any error
set -e

cd "$(dirname "$(realpath $0)")"
pwd

# client setup
cd client
npm install

# server setup
cd ../server
conda create -n autocorrectenv -f environment.yml
conda activate autocorrectenv
npm install
cd python
pip install .
cd ../..

echo "done!"
