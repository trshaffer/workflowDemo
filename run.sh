#!/bin/sh

# lazy option parsing: $1 must be JSON args

makeflow --makeflow-log "$1.makeflowlog" --jx-args makeflows/master_args.jx makeflows/master.jx --jx-args "$@"
