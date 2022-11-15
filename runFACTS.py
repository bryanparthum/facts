import sys
import os
import argparse
import errno
import yaml
from pprint import pprint
import FACTS as facts
from radical.entk import AppManager


def run_experiment(exp_dir, debug_mode):

    expconfig = facts.ParseExperimentConfig(exp_dir)
    experimentsteps = expconfig['experimentsteps']
    # ecfg = expconfig['ecfg']
    workflows = expconfig['workflows']
    climate_data_files = expconfig['climate_data_files']

    # write workflows to yml file
    f = open(os.path.join(exp_dir, 'workflows.yml'), 'w')
    f.write("# automatically generated by runFACTS.py\n")
    f.write("#\n")
    yaml.dump(workflows, f)
    f.close()

    # Print out PST info if in debug mode
    if debug_mode:
        print_experimentsteps(experimentsteps)
        print('')
        print('CLIMATE DATA')
        print('------------')
        pprint(climate_data_files)
        print('')
        print_workflows(workflows)
        # Exit
        sys.exit(0)

    # Does the output directory exist? If not, make it
    try:
        os.makedirs(os.path.join(exp_dir, "output"))
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    # Apply the resource configuration provided by the user
    rcfg_name = expconfig['ecfg']['global-options'].get('rcfg-name')
    rcfg = facts.LoadResourceConfig(exp_dir, rcfg_name)

    # Initialize RCT and the EnTK App Manager
    dburl = 'mongodb://%s:%s@%s:%d/facts' \
            % (rcfg['mongodb'].get('username', ''),
               rcfg['mongodb'].get('password', ''),
               rcfg['mongodb'].get('hostname', 'localhost'),
               rcfg['mongodb'].get('port',     27017))
    os.environ['RADICAL_PILOT_DBURL'] = dburl

    amgr = AppManager(hostname=rcfg['rabbitmq'].get('hostname', ''),
                      username=rcfg['rabbitmq'].get('username', ''),
                      password=rcfg['rabbitmq'].get('password', ''),
                      port=rcfg['rabbitmq'].get('port', 5672),
                      autoterminate=False)

    amgr.resource_desc = rcfg['resource-desc']

    # Load the localization list
    if not os.path.isfile(os.path.join(exp_dir, "location.lst")):
        with open(os.path.join(exp_dir, "location.lst"), 'w') as templocationfile:
            templocationfile.write("New_York\t12\t40.70\t-74.01")
    amgr.shared_data = [os.path.join(exp_dir, "location.lst")]

    for step, pipelines in experimentsteps.items():

        print ("****** STEP: " + step + " ******")
        # Assign the list of pipelines to the workflow
        amgr.workflow = pipelines

        # Run the SLR projection workflow
        amgr.run()

    # Close the application manager
    amgr.terminate()


def print_workflows(workflows):

    for this_workflow in workflows:
        print('WORKFLOW: ', this_workflow)
        print('-----------------')
        pprint(workflows[this_workflow])
        print('')


def print_pipeline(pipelines):

    for p in pipelines:
        print("Pipeline {}:".format(p.name))
        print("################################")
        print(p.as_dict())
        for s in p.stages:
            print("Stage {}:".format(s.name))
            print("============================")
            pprint(s.as_dict())
            for t in s.tasks:
                print("Task {}:".format(t.name))
                print("----------------------------")
                pprint(t.as_dict())


def print_experimentsteps(experimentsteps):

    for this_step in experimentsteps.keys():
        print('EXPERIMENT STEP: ', experimentsteps[this_step])
        print('-----------------')
        print_pipeline(experimentsteps[this_step])
        print('')


if __name__ == "__main__":

    # Initialize the argument parser
    parser = argparse.ArgumentParser(description="The Framework for Assessing Changes To Sea-level (FACTS)")

    # Add arguments for the resource and experiment configuration files
    parser.add_argument('edir', help="Experiment Directory")
    parser.add_argument('--debug', help="Enable debug mode (check that configuration files parse, do not execute)", action="store_true")

    # Parse the arguments
    args = parser.parse_args()

    # Does the experiment directory exist?
    if not os.path.isdir(args.edir):
        print('%s does not exist'.format(args.edir))
        sys.exit(1)

    # Go ahead and try to run the experiment
    run_experiment(args.edir, args.debug)

    #sys.exit(0)
