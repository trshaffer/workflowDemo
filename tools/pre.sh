#!/bin/sh

set -e

mkdir -p $(dirname "$2")
python tools/process_points.py "$1" "$2"
