#!/usr/bin/env bash
# One-click setup for Mac/Linux. Double-click this file (or run
# `./setup.sh` in a terminal) from the project root.
set -e
cd "$(dirname "$0")"

if command -v python3 &>/dev/null; then
    python3 setup.py
elif command -v python &>/dev/null; then
    python setup.py
else
    echo "Python 3 is required but was not found."
    echo "Install it from https://www.python.org/downloads/ and re-run this script."
    exit 1
fi