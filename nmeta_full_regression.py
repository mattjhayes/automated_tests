#!/usr/bin/python

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Run full suite of nmeta regression tests
in an easy automated manner to make regression testing
nmeta updates a breeze...
"""
import datetime
import os
import time
from os.path import expanduser
import sys

#*** Logging imports:
import logging
import logging.handlers
import coloredlogs

#*** Parameters for regression of static classification:
STATIC_REPEATS = 1
STATIC_TESTS = ["constrained-bw-tcp1234", "constrained-bw-tcp5555"]
STATIC_DURATION = 10
STATIC_PLAYBOOK = 'nmeta-full-regression-static-template.yml'
STATIC_PAUSE_SWITCH2CONTROLLER = 30
STATIC_SLEEP = 30

def main(argv):
    """
    Main function of nmeta regression tests.
    Sets up logging, creates the timestamped directory
    and runs functions for the various regression test types
    """
    version = "0.1.0"

    #*** Set up logging:
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    coloredlogs.install(level="DEBUG",
                logger=logger,
                fmt="%(asctime)s.%(msecs)03d %(name)s[%(process)d] " \
           "%(funcName)s %(levelname)s %(message)s", datefmt='%H:%M:%S')
    logger.info("Logging initiated")

    #*** Timestamp for results root directory:
    timenow = datetime.datetime.now()
    timestamp = timenow.strftime("%Y%m%d%H%M%S")
    logger.info("root results timestamp is %s", timestamp)

    #*** Directory base path to write results to:
    home_dir = expanduser("~")
    results_dir = os.path.join(home_dir,
                                   "results/regression/nmeta-full/")
    #*** Ansible Playbook directory:
    playbook_dir = os.path.join(home_dir, 'automated_tests')

    #*** Create root directory for results:
    os.chdir(results_dir)
    logger.debug("creating subdirectory %s", timestamp)
    os.mkdir(timestamp)
    basedir = os.path.join(results_dir, timestamp)
    logger.info("base directory is %s", basedir)

    #*** Run static regression testing:
    regression_static_results = \
                    regression_static(logger, basedir, playbook_dir)    


def regression_static(logger, basedir, playbook_dir):
    """
    Nmeta static classification regression testing
    """
    logger.info("running static regression testing")
    subdir = 'static'
    #*** Create subdirectory to write results to:
    os.chdir(basedir)
    os.mkdir(subdir)
    test_basedir = os.path.join(basedir, subdir)
    playbook = os.path.join(playbook_dir, STATIC_PLAYBOOK)
    logger.debug("playbook is %s", playbook)
    #*** Run tests
    for i in range(STATIC_REPEATS):
        for test in STATIC_TESTS:
            #*** Timestamp for specific test subdirectory:
            timenow = datetime.datetime.now()
            testdir_timestamp = timenow.strftime("%Y%m%d%H%M%S")
            logger.info("running test=%s", test)
            test_dir = os.path.join(test_basedir, test,
                                                    testdir_timestamp)
            if test == "constrained-bw-tcp1234":
                policy_name = "main_policy_regression_static.yaml"
            elif test == "constrained-bw-tcp5555":
                policy_name = "main_policy_regression_static_2.yaml"
            else:
                print "ERROR: unknown test type", test
                sys.exit()
            playbook_cmd = "ansible-playbook " + playbook
            playbook_cmd += " --extra-vars "
            playbook_cmd += "\"duration=" + str(STATIC_DURATION)
            playbook_cmd += " results_dir=" + test_dir + "/"
            playbook_cmd += " policy_name=" + policy_name
            playbook_cmd += " pause1=" + \
                                    str(STATIC_PAUSE_SWITCH2CONTROLLER)
            playbook_cmd += "\""
            logger.debug("playbook_cmd=%s", playbook_cmd)
            logger.info("running Ansible playbook...")
            os.system(playbook_cmd)

            #*** Analyse static regression results:
            logger.info("Reading results in directory %s", test_dir)

            # TBD here:
            file1 = os.path.join(test_dir,
                                'pc1.example.com-1234-iperf_result.txt')
            
            with open(file1) as filehandle:
                data = filehandle.read()
                data = data.split(",")
                print "data is", data
                #*** The result is in position index 8 and has newline:
                result = str(data[8]).rstrip()
                print "result is", result


            logger.info("Sleeping... zzzz")
            time.sleep(STATIC_SLEEP)
    
    #~/results/regression/nmeta-full/20160923220701/static/constrained-bw-tcp1234/20160923220701$ more pc1.example.com-1234-iperf_result.txt

    #20160923220804,10.1.0.1,34237,10.1.0.2,1234,3,0.0-22.9,393216,137364

    #timestamp,source_address,source_port,destination_address,destination_port,interval,transferred_bytes,bits_per_second
    

def get_immediate_subdirectories(base_dir, logger):
    """
    Pass this a function a directory path and it
    will return a list of full-path subdirectories
    off that directory (empty list if none)
    """
    result = []
    for name in os.listdir(base_dir):
        logger.debug("is %s a directory?", name)
        if os.path.isdir(name):
            logger.debug("yes, %s is a directory", name)
            result.append(os.path.join(a_dir, name))
    return result

if __name__ == "__main__":
    #*** Run the main function with command line
    #***  arguments from position 1
    main(sys.argv[1:])
