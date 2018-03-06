# workflowDemo

This version of the Lifemapper Makeflow generator splits a single csv file 
containing multiple taxa but grouped so that like taxa are adjacent to each
other into files.  These files are used as inputs to models if there are
enough points and the projections.

Examples:

    $ python scripts/create_makeflows.py data/points/heuchera.csv data/layers/worldclim data/layers/worldclim 

Creates makeflows for the Heuchera dataset and only one model / projection scenario

    $ python scripts/create_makeflows.py data/points/saxifragales.csv data/layers/worldclim data/layers/worldclim data/layers/mid data/layers/lgm
 
Creates makeflows for the Saxifragales dataset (larger) with a model scenario and three projection scenarios each
