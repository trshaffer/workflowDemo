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
    for _, (taxon, lines) in chunk:
        lines = list(lines)
        if len(lines) < POINTS_THRESHOLD:
            continue
        taxa.append(taxon)
        taxonCsvFn = os.path.join(RAW_POINTS_DIR, '{}.csv'.format(taxon))
        with open(taxonCsvFn, 'w') as outF:
            for tl in lines:
                outF.write(','.join(tl) + '\n')
    chunkFn = os.path.join(os.path.join(MAKEFLOW_DIR,
        'chunk{}.json'.format(chunkNo)))
    with open(chunkFn, 'w') as f:
        json.dump({
            'taxa': taxa,
            'args': chunkFn,
            'model': mdlScn,
            'projections': prjScns,
        }, f)

# .............................................................................
def generate_makeflows(pointsCsv, mdlScn, prjScns, numPerGroup=100):
    """
    @summary: Generate makeflows
    """

    # Loop through points csv and split into individual files
    with open(pointsCsv) as inF:
        lines = ([x.strip() for x in y.split(',')] for y in inF)
        taxa = itertools.groupby(lines, lambda x: x[0])
        chunks = itertools.groupby(enumerate(taxa),
                lambda x: x[0] // numPerGroup)
        for c in chunks:
            write_chunk(c[1], c[0], mdlScn, prjScns)

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
