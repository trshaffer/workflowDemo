#!/bin/sh

set -e

for a in $(ls "$1"); do
  (
    cd "$1/$a"
    for b in $(find . -mindepth 1 -type f -printf '%P\n'); do
      for c in $(seq "$2"); do
        TARGET="../$a.$c/$b"
        mkdir -p $(dirname "$TARGET")
	ln "$b" "$TARGET"
      done
    done
  )
done
