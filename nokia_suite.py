import os

# location of this job file
mypath = os.path.dirname(__file__)

def main(runtime):
    'main entry point for a job is the main() function'

    # set script file 
    script = os.path.join(mypath, 'nokia_tests.py')

    # run script as a task under this job
    # if --testbed-file is provided, the corresponding loaded 'testbed'
    # object will be passed to each script within this job automatically
    runtime.tasks.run(script)
