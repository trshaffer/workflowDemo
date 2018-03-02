#!/bin/sh

makeflow --jx-args raw_points/index.json --jx-define 'model_scenario="data/layers/worldclim"' --jx-define 'projection_scenarios="[\"data/layers/worldclim\"]"' --jx-args scripts/master_args.jx scripts/master.jx
