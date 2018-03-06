#!/bin/sh

# pass in the arguments for this run, e.g.
#     --jx-args makeflows/chunk0.json

makeflow --jx-args makeflows/master_args.jx makeflows/master.jx "$@"
