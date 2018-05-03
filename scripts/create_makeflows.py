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
OUTPUT_DIR = 'outputs'
POINTS_THRESHOLD = 30 # The threshold at which to compute models


def write_chunk(chunk, chunkFn, mdlScn, prjScns):
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
    with open(chunkFn, 'w') as f:
        json.dump({
            'taxa': taxa,
            'args': chunkFn,
            'model': mdlScn,
            'projections': prjScns,
        }, f, indent=4)
    return taxa

# .............................................................................
def generate_makeflows(pointsCsv, mdlScn, prjScns, numPerGroup):
    """
    @summary: Generate makeflows
    """

    proj = [os.path.basename(x.rstrip('/')) for x in prjScns]

    master = {
        "rules": [],
        "categories": {
            "default": {
                "resources": {
                    "cores": len(prjScns),
                    "memory": 4096 * len(prjScns),
                    "disk": 4096 * len(prjScns),
                },
            },
        },
    }

    # Loop through points csv and split into individual files
    with open(pointsCsv) as inF:
        lines = ([x.strip() for x in y.split(',')] for y in inF)
        taxa = itertools.groupby(lines, lambda x: x[0])
        chunks = itertools.groupby(enumerate(taxa),
                lambda x: x[0] // numPerGroup if numPerGroup else 0)
        for c in chunks:
            chunkFn = os.path.join(os.path.join(MAKEFLOW_DIR,
                'chunk{}.json'.format(c[0])))
            taxa = write_chunk(c[1], chunkFn, mdlScn, prjScns)
            log_files = ["{}.debug".format(chunkFn), "{}.makeflowlog".format(chunkFn), "{}.wqlog".format(chunkFn), "{}.wqlog.tr".format(chunkFn)]
            master['rules'].append({
                "command": "makeflow -dall -o {}.debug -l {}.makeflowlog -L {}.wqlog --jx-context makeflows/params.jx --jx-context {} makeflows/taxa.jx ".format(chunkFn, chunkFn, chunkFn, chunkFn, chunkFn) + ' '.join(["&& touch {}".format(x) for x in log_files]),
                "inputs": list(set([mdlScn] + prjScns)) + ['makeflows/params.jx', 'makeflows/taxa.jx', chunkFn, 'apps/', 'tools/'] + ['raw_points/{}.csv'.format(t) for t in taxa],
                "outputs": list(set([os.path.join(OUTPUT_DIR, t, 'proj_' + p, '{}_{}.asc'.format(t, p)) for t in taxa for p in proj]))
                    + log_files,
            })

    with open(os.path.join(MAKEFLOW_DIR, 'master.json'), "w") as f:
        json.dump(master, f, indent=4)

# .............................................................................
if __name__ == '__main__':

    parser = argparse.ArgumentParser(
            'This script generates makeflows to process the input data')

    parser.add_argument('--split', type=int,
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
            args.proj_scenario, args.split)
