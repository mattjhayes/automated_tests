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
Run performance (no load) tests against different numbers of
in-path switches, using a chosen controller app type.
"""

#*** For writing to file:
from __future__ import print_function

import datetime
import time
import os
from os.path import expanduser
import sys

VERSION = "0.1.0"

#*** How many times to run the set of tests:
REPEATS = 3

#*** Max number of switches in path
SWITCHES_MAX = 4

#*** Types of controller app tests to run. Choose one or more of:
# ["nmeta2-active", "nmeta2-passive", "nosdn"]
TESTS = ["nmeta2-active", "nmeta2-passive", "nosdn"]

#*** Timestamp for results root directory:
TIMENOW = datetime.datetime.now()
TIMESTAMP = TIMENOW.strftime("%Y%m%d%H%M%S")
print ("timestamp is", TIMESTAMP)

#*** Directory base path to write results to:
HOME_DIR = expanduser("~")
RESULTS_DIR = os.path.join(HOME_DIR,
                   "results/multi-switch-performance-no-load/")

#*** Create root directory for results:
os.chdir(RESULTS_DIR)
os.mkdir(TIMESTAMP)
TEST_BASEDIR = os.path.join(RESULTS_DIR, TIMESTAMP)
print ("TEST_BASEDIR is", TEST_BASEDIR)

#*** Filenames for test suite output into test root directory:
FILENAME_SWITCH_SETUP_RESULTS = "switch_topology_setup_results.csv"

#*** Ansible Playbooks to use:
PLAYBOOK_TEST = os.path.join(HOME_DIR, \
            "automated_tests/performance-no-load-tests-template.yml")
PLAYBOOK_SINGLE_SWITCH_SETUP = os.path.join(HOME_DIR, \
            "automated_tests/multi-switch-setup-single-switch.yml")
PLAYBOOK_DUAL_SWITCH_SETUP = os.path.join(HOME_DIR, \
            "automated_tests/multi-switch-setup-dual-switch.yml")
PLAYBOOK_TRIPLE_SWITCH_SETUP = os.path.join(HOME_DIR, \
            "automated_tests/multi-switch-setup-triple-switch.yml")
PLAYBOOK_QUAD_SWITCH_SETUP = os.path.join(HOME_DIR, \
            "automated_tests/multi-switch-setup-quad-switch.yml")

def main():
    """
    Main function
    """
    switches = 1

    #*** Run tests
    for i in range(1, REPEATS + 1):
        for switches in range(1, SWITCHES_MAX + 1):
            #*** Set switches up appropriate to test type:
            print ("Setting environment up for ", switches,
                                                    "switch tests")
            if switches == 1:
                playbook_cmd = "ansible-playbook " + \
                                            PLAYBOOK_SINGLE_SWITCH_SETUP
            elif switches == 2:
                playbook_cmd = "ansible-playbook " + \
                                              PLAYBOOK_DUAL_SWITCH_SETUP
            elif switches == 3:
                playbook_cmd = "ansible-playbook " + \
                                            PLAYBOOK_TRIPLE_SWITCH_SETUP
            elif switches == 4:
                playbook_cmd = "ansible-playbook " + \
                                              PLAYBOOK_QUAD_SWITCH_SETUP
            else:
                print ("ERROR: unknown number of switches", switches)
                sys.exit()
            #*** Run playbook to set up switches:
            result = os.system(playbook_cmd)
            result = "switches=" + str(switches) + "," + "iteration=" \
                            + str(i) + "," + "result=" + str(result)
            write_result(FILENAME_SWITCH_SETUP_RESULTS, result)
            #*** Only use DPAE n if two or more switches:
            if switches > 1:
                start_dpn = 1
            else:
                start_dpn = 0
            #*** Iterate through the test types:
            for test_type in TESTS:
                print ("Iteration", i, "of", test_type, "on",
                        switches, "switches")
                test_dir = os.path.join(TEST_BASEDIR, str(switches),
                                                            test_type)
                #*** Set up the playbook to run the test:
                if test_type == "nmeta":
                    start_nmeta = "true"
                    start_nmeta2 = "false"
                    nmeta2_mode = "none"
                    start_simple_switch = "false"
                elif test_type == "nmeta2-active":
                    start_nmeta = "false"
                    start_nmeta2 = "true"
                    nmeta2_mode = "active"
                    start_simple_switch = "false"
                elif test_type == "nmeta2-passive":
                    start_nmeta = "false"
                    start_nmeta2 = "true"
                    nmeta2_mode = "passive"
                    start_simple_switch = "false"
                elif test_type == "simpleswitch":
                    start_nmeta = "false"
                    start_nmeta2 = "false"
                    nmeta2_mode = "none"
                    start_simple_switch = "true"
                elif test_type == "nosdn":
                    start_nmeta = "false"
                    start_nmeta2 = "false"
                    nmeta2_mode = "none"
                    start_simple_switch = "false"
                else:
                    print ("ERROR: unknown test type", test_type)
                    sys.exit()
                playbook_cmd = "ansible-playbook " + PLAYBOOK_TEST
                playbook_cmd += " --extra-vars "
                playbook_cmd += "\"start_nmeta=" + start_nmeta
                playbook_cmd += " start_nmeta2=" + start_nmeta2
                playbook_cmd += " start_simple_switch=" + start_simple_switch
                playbook_cmd += " nmeta2_mode=" + nmeta2_mode
                playbook_cmd += " results_dir=" + test_dir + "/"
                playbook_cmd += "\""
                print ("playbook_cmd is", playbook_cmd)

                print ("running Ansible playbook...")
                os.system(playbook_cmd)
                print ("Sleeping... zzzz")
                time.sleep(30)

def write_result(filename, value):
    """
    Write a result value to a file (appends)
    """
    print ("Writing result", value, "to file")
    result_filename = os.path.join(TEST_BASEDIR, filename)
    with open(result_filename, 'a') as f:
        print(value, file=f)

if __name__ == '__main__':
    main()
