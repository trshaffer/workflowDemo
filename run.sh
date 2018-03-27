#!/bin/sh

# lazy option parsing: $1 must be JSON args

/scratch365/tshaffe1/cctools/makeflow/src/makeflow --makeflow-log "$1.makeflowlog" --jx-args makeflows/master_args.jx makeflows/master.jx --jx-args "$@"
