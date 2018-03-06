"""
@summary: This script will create Makeflow documents for the input data
"""

import itertools
import argparse
import json
import os

# .............................................................................
# .                                 Constants                                 .
# .............................................................................
MAKEFLOW_DIR = 'makeflows' # Directory to write makeflows
RAW_POINTS_DIR = 'raw_points' # Directory to write raw point CSVs
POINTS_THRESHOLD = 30 # The threshold at which to compute models


def write_chunk(chunk, chunkNo, mdlScn, prjScns):
    taxa = []
    for taxon in chunk:
        taxa.append(taxon[0][0])
        taxonCsvFn = os.path.join(RAW_POINTS_DIR, '{}.csv'.format(taxa[-1]))
        with open(taxonCsvFn, 'w') as outF:
            for tl in taxon:
                outF.write(tl)
    chunkFn = os.path.join(os.path.join(MAKEFLOW_DIR,
        'chunk{}.json'.format(chunkNo)))
    with open(chunkFn, 'w') as f:
        json.dump({
            'taxa': taxa,
            'model_scenario': mdlScn,
            'projection_scenarios': prjScns,
        }, f)

# .............................................................................
def generate_makeflows(pointsCsv, mdlScn, prjScns, numPerGroup=100):
    """
    @summary: Generate makeflows
    """

    # Loop through points csv and split into individual files
    with open(pointsCsv) as inF:
        lines = (x.split(',') for x in inF)
        taxa = itertools.groupby(lines, lambda x: x[0])
        good_taxa = (x for x in taxa if len(x) >= POINTS_THRESHOLD)
        chunks = itertools.groupby(enumerate(good_taxa),
                lambda x: x[0] // numPerGroup)
        for c in chunks:
            write_chunk(c[1], c[0] // numPerGroup, mdlScn, prjScns)

# .............................................................................
if __name__ == '__main__':

    parser = argparse.ArgumentParser(
            'This script generates makeflows to process the input data')

    parser.add_argument('-g', type=int, default=100,
            help='How many makeflows should be included in each group')

    parser.add_argument('points_csv', type=str,
            help='A CSV file containing occurrence information. ' \
            + 'Like taxa should be in consecutive rows.')
    parser.add_argument('model_scenario', type=str,
            help='The scenario directory that should be used for modeling')
    parser.add_argument('proj_scenario', type=str, nargs='*',
            help='Scenario directory that should be use for projections')
    args = parser.parse_args()

    generate_makeflows(args.points_csv, args.model_scenario,
            args.proj_scenario, numPerGroup=args.g)
