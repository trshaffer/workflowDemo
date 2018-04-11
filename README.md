# workflowDemo

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

    python scripts/create_makeflows.py data/points/saxifragales.csv data/layers/worldclim data/layers/worldclim data/layers/mid data/layers/lgm

Since there are more data points, the generated workflow is split into
several parts.
Each one is run separately, just as in the small example.
If you like, you could use a master Makeflow to launch each piece.
