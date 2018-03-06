#!/bin/sh

makeflow --jx-args raw_points/index.json --jx-define 'scenarios="scripts/scenarios.json"' --jx-args scripts/master_args.jx scripts/master.jx
