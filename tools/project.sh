#!/bin/sh
set -e

mkdir -p $(dirname "$3")
./tools/java8_run \
    -cp apps/maxent.jar density.Project \
    "$1" "$2" "$3" \
    nowarnings nocache autorun -z \
    || true
touch "$3"
