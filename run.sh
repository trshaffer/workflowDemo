#!/bin/sh

# lazy option parsing: $1 must be JSON args

cd /scratch365/tshaffe1/workflowDemo

#exec > $(mktemp "../tmp/$(basename $1)".XXXXXX) 2>&1

../cctools/makeflow/src/makeflow --makeflow-log "$1.makeflowlog" --jx-args makeflows/master_args.jx makeflows/master.jx --jx-args "$@"
