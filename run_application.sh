#!/bin/bash

# exit on error
set -e

cd "$(dirname "$(realpath $0)")"
sudo npm install -g concurrently
concurrently "cd server; npm run dev" "cd client; npm run dev"
