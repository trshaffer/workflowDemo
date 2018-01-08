"""
@summary: This script will create Makeflow documents for the input data
"""

import argparse
import os

# .............................................................................
# .                                 Constants                                 .
# .............................................................................
MAKEFLOW_DIR = 'makeflows' # Directory to write makeflows
RAW_POINTS_DIR = 'raw_points' # Directory to write raw point CSVs
OUTPUT_DIR = 'outputs'
TOUCHFILE_DIR = 'touch'
POINTS_DIR = 'points' # Directory to store processed points 
POINTS_THRESHOLD = 30 # The threshold at which to compute models
MAXENT = 'apps/maxent.jar'

SUB_MAKEFLOW_HEADERS = ['MAXENT={}'.format(MAXENT)]
MASTER_MAKEFLOW_HEADERS = []


# .............................................................................
class MfRule(object):
   """
   @summary: Class to create commands for a makeflow document
   """
# .............................................................................
# Constructor
# .............................................................................
   def __init__(self, command, targets, dependencies=None, comment=''):
      """
      @summary Constructor for commands used by Makeflow
      @param command: string used by LmCompute to compute this object
      @param targets: list of outputs for this object
      @param dependencies: list of dependencies for this object
      @param comment: A comment that can be added to a Makeflow document for 
                         clarity
      """
      self.command = command
      self.targets = targets
      if dependencies is None:
         self.dependencies = []
      else:
         self.dependencies = dependencies
      self.comment = comment

# .............................................................................
def write_rules(dag_fn, rules, headers=None):
   """
   @summary: Write rules to Makeflow DAG file
   @param dag_fn: The location to write the Makeflow DAG
   @param rules: A list of rules to write
   @param headers: If this is a list, write each entry on a line in DAG
   """
   with open(dag_fn, 'w') as outF:
      
      if headers is not None:
         for h in headers:
            outF.write('{}\n'.format(h))
      
      for rule in rules:
         outF.write('# {}\n'.format(rule.comment))
         outF.write('{} : {}\n'.format(' '.join(rule.targets), 
                                       ' '.join(rule.dependencies)))
         outF.write('   {}\n\n'.format(rule.command))

# .............................................................................
def get_sub_makeflow(taxon, taxonCsvFn, numPoints, modelScenario, projectionScenarios):
   """
   @summary: Returns a list of rules for processing a particular taxon
   """
   rules = []
   taxonDir = os.path.join(OUTPUT_DIR, taxon)
   # Create taxon directory command
   taxonTouchFn = os.path.join(taxonDir, 'touch.out')
   createTaxDirCmd = 'mkdir {} ; touch {}'.format(taxonDir, taxonTouchFn)
   rules.append(MfRule(createTaxDirCmd, [taxonTouchFn]))
      
   outTaxonCsvFn = os.path.join(taxonDir, '{}.csv'.format(taxon))
   procPointsCmd = 'python tools/process_points.py {} {}'.format(taxonCsvFn, 
                                                                 outTaxonCsvFn)
   rules.append(MfRule(procPointsCmd, [outTaxonCsvFn], dependencies=[
                                                   taxonCsvFn, taxonTouchFn]))
   # Process points
   if numPoints >= POINTS_THRESHOLD:
      mdlWorkDir = os.path.join(taxonDir, 'model')
      # Create model directory command
      mdlTouchFn = os.path.join(mdlWorkDir, 'touch.out')
      createMdlDirCmd = 'mkdir {} ; touch {}'.format(mdlWorkDir, mdlTouchFn)
      rules.append(MfRule(createMdlDirCmd, [mdlTouchFn], 
                          dependencies=[taxonTouchFn]))
      
      ruleset = os.path.join(mdlWorkDir, '{}.lambdas'.format(taxon))
      modelTargets = [ruleset]
      mdlCmd = 'java -cp $MAXENT {} -s {} -e {} -o {} nowarnings nocache autorun -z'.format(
                  'density.MaxEnt', outTaxonCsvFn, modelScenario, 
                  mdlWorkDir)
      rules.append(MfRule(mdlCmd, modelTargets, 
                   dependencies=[MAXENT, outTaxonCsvFn, mdlTouchFn]))

      for prjScn in projectionScenarios:
         prjWorkDir = os.path.join(taxonDir, 'proj_{}'.format(
                                                   os.path.basename(prjScn)))
         # Create projection directory command
         prjTouchFn = os.path.join(prjWorkDir, 'touch.out')
         createPrjDirCmd = 'mkdir {} ; touch {}'.format(prjWorkDir, prjTouchFn)
         rules.append(MfRule(createPrjDirCmd, [prjTouchFn], dependencies=[mdlTouchFn]))
      
         prjOutFn = os.path.join(prjWorkDir, '{}_{}.asc'.format(taxon, 
                                                     os.path.basename(prjScn)))
         prjTargets = [prjOutFn]
         prjCmd = 'java -cp $MAXENT {} {} {} {} nowarnings nocache autorun -z'.format(
                        'density.Project', ruleset, prjScn, prjOutFn)
         rules.append(MfRule(prjCmd, prjTargets, dependencies=[MAXENT, 
                                                         ruleset, prjTouchFn]))
   
   return rules

# .............................................................................
def generate_makeflows(pointsCsv, mdlScn, prjScns, numPerGroup=100):
   """
   @summary: Generate makeflows
   """
   currentTaxon = None
   taxonLines = []
   masterMfRules = []
   
   i = 0 # Number of sub-makeflows in this master
   j = 0 # Current master makeflow number
   
   masterMfF = open(os.path.join(MAKEFLOW_DIR, 'master_{}.dag'.format(j)), 'w')
   
   # Loop through points csv and split into individual files
   with open(pointsCsv) as inF:
      for line in inF:
         try:
            taxon, x, y = line.strip().split(',')
            # Check if initial
            if currentTaxon is None:
               currentTaxon = taxon
          
            # If we have encountered a new taxon, write old and start new
            if currentTaxon != taxon:
               
               numTaxonPoints = len(taxonLines)
               taxonCsvFn = os.path.join(RAW_POINTS_DIR, '{}.csv'.format(currentTaxon))
               with open(taxonCsvFn, 'w') as outF:
                  for tl in taxonLines:
                     outF.write(tl)
               
               # Add sub-makeflow to master
               subMakeflowFn = os.path.join(MAKEFLOW_DIR, '{}.dag'.format(currentTaxon))
               touchFn = os.path.join(TOUCHFILE_DIR, '{}.touch'.format(currentTaxon))
               write_rules(subMakeflowFn,
                           get_sub_makeflow(currentTaxon, taxonCsvFn, 
                                            numTaxonPoints, mdlScn, 
                                            prjScns),
                           headers=SUB_MAKEFLOW_HEADERS)
               
               # TODO: Add makeflow options here
               mfCmd = 'LOCAL makeflow {} ; touch {}'.format(subMakeflowFn, touchFn)
               # TODO: Need to register the taxon DAG somewhere (subMakeflowFn)
               masterMfRules.append(MfRule(mfCmd, [touchFn], dependencies=[]))
               
               i += 1
               # Check if we should rotate master makeflow
               if i == numPerGroup:
                  i = 0
                  write_rules(os.path.join(MAKEFLOW_DIR, 'master_{}.dag'.format(j)),
                              masterMfRules, headers=MASTER_MAKEFLOW_HEADERS)
                  masterMfRules = []
                  j += 1
               
               # Reset variables
               taxonLines = [line]
               currentTaxon = taxon
   
            else:
               # Add this line to our taxon lines
               taxonLines.append(line)
         except Exception, e:
            print str(e)
            print line
      # Need to write out last one
      with open(os.path.join(RAW_POINTS_DIR, '{}.csv'.format(taxon)), 'w') as outF:
         for tl in taxonLines:
            outF.write(tl)
            subMakeflowFn = os.path.join(MAKEFLOW_DIR, '{}.dag'.format(taxon))
            touchFn = os.path.join(TOUCHFILE_DIR, '{}.touch'.format(taxon))
            write_rules(subMakeflowFn,
                        get_sub_makeflow(taxon, taxonCsvFn, numTaxonPoints, mdlScn, 
                                         prjScns),
                        headers=SUB_MAKEFLOW_HEADERS)
   
   if len(masterMfRules) > 0:
      write_rules(os.path.join(MAKEFLOW_DIR, 'master_{}.dag'.format(j)),
                           masterMfRules, headers=MASTER_MAKEFLOW_HEADERS)
            
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
   
   generate_makeflows(args.points_csv, args.model_scenario, args.proj_scenario, 
                      numPerGroup=args.g)
   