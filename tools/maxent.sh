#!/bin/sh

set -e

mkdir -p "$3"
./tools/java8_run \
    -cp apps/maxent.jar density.MaxEnt \
    -s "$1" -e "$2" -o "$3" \
    nowarnings nocache autorun -z \
    || true
touch "$4"
