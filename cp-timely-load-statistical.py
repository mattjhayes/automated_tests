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
Run nmeta and nmeta2 statistical TC Control Plane (CP)
timeliness tests.

How quickly is a new MAC learnt and
instantiated as Data Plane forwarding entries under
varying levels of New Flow Per Second (NFPS) load?

"""
import datetime
import time
import os
from os.path import expanduser
import sys

version = "0.1.0"

#*** How many times to run the set of tests:
repeats = 3

#*** Types of tests to run:
tests = ["nmeta2-active", "nmeta2-passive", "simpleswitch", "nmeta"]

#*** Directory base path to write results to:
home_dir = expanduser("~")
results_dir = os.path.join(home_dir,
                                "results/timeliness/controlplane/")

#*** Parameters for repetition of tests with different filt rate:
test_load_initial_rate = 10
test_load_rate_increment = 10
test_load_max_rate = 60

#*** Parameters for filt new flow rate load test:
target_ip = "10.1.0.7"
target_mac = "08:00:27:40:e4:4c"
interface = "eth1"
flow_inc = "5"
incr_interval = "1"
proto = "6"
dport = "12345"
algorithm = "make-good"

#*** Crafted MAC:
crafted_mac = "00:00:00:00:12:34"

#*** Ansible Playbook to use:
playbook = os.path.join(home_dir, \
                    "automated_tests/cp-timely-load-template.yml")

#*** Timestamp for results root directory:
timenow = datetime.datetime.now()
timestamp = timenow.strftime("%Y%m%d%H%M%S")
print "timestamp is", timestamp

#*** Create root directory for results:
os.chdir(results_dir)
os.mkdir(timestamp)
test_basedir = os.path.join(results_dir, timestamp)
print "test_basedir is", test_basedir

#*** Create sub folders
os.chdir(test_basedir)
for test in tests:
    os.mkdir(test)

#*** Initialise:
start_nmeta = "false"
start_nmeta2 = "false"

#*** Run tests:
test_load_rate = test_load_initial_rate
for i in range(repeats):
    while test_load_rate <= test_load_max_rate:
        for test in tests:
            print "running test", test
            test_dir = os.path.join(test_basedir, test)
            if test == "nmeta":
                start_nmeta = "true"
                start_nmeta2 = "false"
                nmeta2_mode = "none"
                start_simple_switch = "false"
                policy_name = "main_policy_regression_statistical.yaml"
            elif test == "nmeta2-active":
                start_nmeta = "false"
                start_nmeta2 = "true"
                nmeta2_mode = "active"
                start_simple_switch = "false"
                policy_name = "main_policy_regression_statistical.yaml"
            elif test == "nmeta2-passive":
                start_nmeta = "false"
                start_nmeta2 = "true"
                nmeta2_mode = "passive"
                start_simple_switch = "false"
                policy_name = "main_policy_regression_statistical_passive.yaml"
            elif test == "simpleswitch":
                start_nmeta = "false"
                start_nmeta2 = "false"
                nmeta2_mode = "none"
                start_simple_switch = "true"
                policy_name = " none"
            else:
                print "ERROR: unknown test type", test
                sys.exit()
            playbook_cmd = "ansible-playbook " + playbook + " --extra-vars "
            playbook_cmd += "\"start_nmeta=" + start_nmeta
            playbook_cmd += " start_nmeta2=" + start_nmeta2
            playbook_cmd += " start_simple_switch=" + start_simple_switch
            playbook_cmd += " test_type=" + test
            playbook_cmd += " results_dir=" + test_dir + "/"
            playbook_cmd += " target_ip=" + target_ip
            playbook_cmd += " target_mac=" + target_mac
            playbook_cmd += " interface=" + interface
            playbook_cmd += " initial_rate=" + str(test_load_rate)
            playbook_cmd += " max_rate=" + str(test_load_rate)
            playbook_cmd += " flow_inc=" + str(test_load_rate_increment)
            playbook_cmd += " incr_interval=" + incr_interval
            playbook_cmd += " proto=" + proto
            playbook_cmd += " dport=" + dport
            playbook_cmd += " algorithm=" + algorithm
            playbook_cmd += " policy_name=" + policy_name
            playbook_cmd += " crafted_mac=" + crafted_mac
            playbook_cmd += "\""
            print "playbook_cmd is", playbook_cmd

            print "running Ansible playbook..."
            os.system(playbook_cmd)
            print "Sleeping... zzzz"
            time.sleep(30)

    test_load_rate = test_load_rate + test_load_rate_increment
