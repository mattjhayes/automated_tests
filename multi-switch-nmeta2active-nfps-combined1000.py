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
Run baseline tests
"""

#*** For writing to file:
from __future__ import print_function

import datetime
import time
import os
from os.path import expanduser
import sys

version = "0.1.1"

#*** How many times to run the set of tests:
REPEATS = 3

#*** Timestamp for results root directory:
timenow = datetime.datetime.now()
TIMESTAMP = timenow.strftime("%Y%m%d%H%M%S")
print ("timestamp is", TIMESTAMP)

#*** Directory base path to write results to:
HOME_DIR = expanduser("~")
RESULTS_DIR = os.path.join(HOME_DIR,
                   "results/nfps-load-tests/multi-switch-nmeta2active/")

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

    #*** Types of tests to run (number of switches in path):
    tests = ["single", "dual"]

    #*** Parameters for filt new flow rate load test:
    target_ip = "10.1.0.7"
    target_mac = "08:00:27:40:e4:4c"
    interface = "eth1"
    initial_rate = "10"
    max_rate = "1000"
    flow_inc = "10"
    incr_interval = "1"
    proto = "6"
    dport = "12345"
    algorithm = "make-good"

    #*** Ansible Playbooks to use:
    playbook = os.path.join(HOME_DIR, \
            "automated_tests/multi-switch-nfps-load-tests-template.yml")
    playbook_single_switch = os.path.join(HOME_DIR, \
            "automated_tests/multi-switch-setup-single-switch.yml")
    playbook_dual_switch = os.path.join(HOME_DIR, \
            "automated_tests/multi-switch-setup-dual-switch.yml")

    #*** Create sub folders
    os.chdir(TEST_BASEDIR)
    for test in tests:
        os.mkdir(test)

    #*** Specific to running nmeta2 in active mode:
    start_nmeta = "false"
    start_nmeta2 = "true"
    nmeta2_mode = "active"
    start_simple_switch = "false"

    #*** Start DPAE n (dpn) in tests that have multiple switches:
    start_dpn = 0

    #*** Run tests
    for i in range(REPEATS):
        for test in tests:
            print ("running test", test, "test suite iteration", i+1, \
                                                        "of", REPEATS)
            test_dir = os.path.join(TEST_BASEDIR, test)
            #*** Set switches up appropriate to test type:
            if test == "single":
                playbook_cmd = "ansible-playbook " + playbook_single_switch
                result = os.system(playbook_cmd)
                result = test + "," + str(i+1) + "," + str(result)
                write_result(FILENAME_SWITCH_SETUP_RESULTS, result)
            elif test == "dual":
                playbook_cmd = "ansible-playbook " + playbook_dual_switch
                result = os.system(playbook_cmd)
                result = test + "," + str(i+1) + "," + str(result)
                write_result(FILENAME_SWITCH_SETUP_RESULTS, result)
                start_dpn = 1
            else:
                print ("ERROR: unknown test type", test)
                sys.exit()
            playbook_cmd = ""
            playbook_cmd = "ansible-playbook " + playbook + " --extra-vars "
            playbook_cmd += "\"start_nmeta=" + start_nmeta
            playbook_cmd += " start_nmeta2=" + start_nmeta2
            playbook_cmd += " start_simple_switch=" + start_simple_switch
            playbook_cmd += " nmeta2_mode=" + nmeta2_mode
            playbook_cmd += " start_dpn=" + start_dpn
            playbook_cmd += " results_dir=" + test_dir + "/"
            playbook_cmd += " target_ip=" + target_ip
            playbook_cmd += " target_mac=" + target_mac
            playbook_cmd += " interface=" + interface
            playbook_cmd += " initial_rate=" + initial_rate
            playbook_cmd += " max_rate=" + max_rate
            playbook_cmd += " flow_inc=" + flow_inc
            playbook_cmd += " incr_interval=" + incr_interval
            playbook_cmd += " proto=" + proto
            playbook_cmd += " dport=" + dport
            playbook_cmd += " algorithm=" + algorithm
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
