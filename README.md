# Lifemapper

This version of the Lifemapper Makeflow generator splits a single csv file 
containing multiple taxa but grouped so that like taxa are adjacent to each
other into files.  These files are used as inputs to models if there are
enough points and the projections.

## Small Example

This example processes the Heuchera dataset and only one model /
projection scenario.

    python scripts/create_makeflows.py data/points/heuchera.csv data/layers/worldclim data/layers/worldclim 

This dataset is small enough that it all runs in one master Makeflow.
To run it, make sure Makeflow is in your `$PATH` and run

    makeflow --jx-context makeflows/params.jx --jx-context makeflows/chunk0.json makeflows/taxa.jx

## Larger Example

This example runs on the Saxifragales dataset (larger) with a model scenario
and three projection scenarios each

    python scripts/create_makeflows.py data/points/saxifragales.csv data/layers/worldclim data/layers/*

Since there are more data points, the generated workflow can be split into
several parts.
Use the `--split` option to specify the maximum number of taxa to put in each chunk.
Each one is run separately, just as in the small example.
A Makeflow to run all the chunks is generated at `makeflows/master.json`.
Since we're running recursive invocations of Makeflow,
we need to put each chunk in a sandbox.
To run the master workflow, do

    makeflow --sandbox --json makeflows/master.json

## Even Larger

The `dup.sh` script can duplicate layers under different filenames to increase
the scale of the workflow without actually using new data. To make four
duplicates of the layers (for a total of five of each), run

    ./dup.sh data/layers/ 4

You'll need to run the Python line from the Large example.
