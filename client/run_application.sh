#!/bin/bash

# exit on error
set -e

cd "$(dirname "$(realpath $0)")"

npm install -g concurrently
concurrently "cd ../server; npm run dev" "npm run dev"
