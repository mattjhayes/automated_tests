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
in-path switches
"""

#*** For writing to file:
from __future__ import print_function

import datetime
import time
import os
from os.path import expanduser
import sys

version = "0.1.0"

#*** How many times to run the set of tests:
REPEATS = 3

#*** Types of tests to run:
TESTS = ["nmeta2-active", "nmeta2-passive", "nosdn"]

#*** Timestamp for results root directory:
timenow = datetime.datetime.now()
TIMESTAMP = timenow.strftime("%Y%m%d%H%M%S")
print ("timestamp is", TIMESTAMP)

#*** Directory base path to write results to:
HOME_DIR = expanduser("~")
RESULTS_DIR = os.path.join(HOME_DIR,
                   "results/nfps-load-tests/multi-switch-performance-no-load/")

#*** Create root directory for results:
os.chdir(RESULTS_DIR)
os.mkdir(TIMESTAMP)
TEST_BASEDIR = os.path.join(RESULTS_DIR, TIMESTAMP)
print ("TEST_BASEDIR is", TEST_BASEDIR)

#*** Filenames for test suite output into test root directory:
FILENAME_SWITCH_SETUP_RESULTS = "switch_topology_setup_results.csv"

def main():
    """
    Main function
    """

    #*** Ansible Playbook to use:
    playbook = os.path.join(HOME_DIR, \
            "automated_tests/performance-no-load-tests-template.yml")
    playbook_single_switch = os.path.join(HOME_DIR, \
            "automated_tests/multi-switch-setup-single-switch.yml")
    playbook_dual_switch = os.path.join(HOME_DIR, \
            "automated_tests/multi-switch-setup-dual-switch.yml")

    #*** Create sub folders
    os.chdir(TEST_BASEDIR)
    for test in TESTS:
        os.mkdir(test)

    #*** Run tests
    for i in range(REPEATS):
        for test in TESTS:
            print ("running test", test, "test suite iteration", i+1, \
                                                        "of", REPEATS)
            test_dir = os.path.join(TEST_BASEDIR, test)
            if test == "nmeta":
                start_nmeta = "true"
                start_nmeta2 = "false"
                nmeta2_mode = "none"
                start_simple_switch = "false"
            elif test == "nmeta2-active":
                start_nmeta = "false"
                start_nmeta2 = "true"
                nmeta2_mode = "active"
                start_simple_switch = "false"
            elif test == "nmeta2-passive":
                start_nmeta = "false"
                start_nmeta2 = "true"
                nmeta2_mode = "passive"
                start_simple_switch = "false"
            elif test == "simpleswitch":
                start_nmeta = "false"
                start_nmeta2 = "false"
                nmeta2_mode = "none"
                start_simple_switch = "true"
            elif test == "nosdn":
                start_nmeta = "false"
                start_nmeta2 = "false"
                nmeta2_mode = "none"
                start_simple_switch = "false"
            else:
                print ("ERROR: unknown test type", test)
                sys.exit()
            playbook_cmd = "ansible-playbook " + playbook + " --extra-vars "
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
