#!/bin/sh
set -e

pip install --upgrade pip
pip3 install --no-cache-dir -r install/requirements.txt
pip3 install --no-cache-dir -r install/requirements-dev.txt