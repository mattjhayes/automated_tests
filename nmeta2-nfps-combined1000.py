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
import datetime
import time
import os
from os.path import expanduser
import sys

version = "0.2.0"

#*** How many times to run the set of tests:
repeats = 10

#*** Types of tests to run:
tests = ["nmeta2-active", "nmeta2-passive", "simpleswitch", "nosdn", "nmeta"]

#*** Directory base path to write results to:
home_dir = expanduser("~")
results_dir = os.path.join(home_dir, "results/nfps-load-tests/nmeta2-combined/")

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

#*** Ansible Playbook to use:
playbook = os.path.join(home_dir, \
            "automated_tests/nfps-load-tests-template.yml")

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

#*** Run tests
for i in range(repeats):
    for test in tests:
        print "running test", test
        test_dir=os.path.join(test_basedir, test)
        if test == "nmeta":
            start_nmeta="true"
            start_nmeta2="false"
            nmeta2_mode="none"
            start_simple_switch="false"
        elif test == "nmeta2-active":
            start_nmeta="false"
            start_nmeta2="true"
            nmeta2_mode="active"
            start_simple_switch="false"
        elif test == "nmeta2-passive":
            start_nmeta="false"
            start_nmeta2="true"
            nmeta2_mode="passive"
            start_simple_switch="false"
        elif test == "simpleswitch":
            start_nmeta="false"
            start_nmeta2="false"
            nmeta2_mode="none"
            start_simple_switch="true"
        elif test == "nosdn":
            start_nmeta="false"
            start_nmeta2="false"
            nmeta2_mode="none"
            start_simple_switch="false"
        else:
            print "ERROR: unknown test type", test
            sys.exit()
        playbook_cmd = "ansible-playbook " + playbook + " --extra-vars "
        playbook_cmd += "\"start_nmeta=" + start_nmeta
        playbook_cmd += " start_nmeta2=" + start_nmeta2
        playbook_cmd += " start_simple_switch=" + start_simple_switch
        playbook_cmd += " nmeta2_mode=" + nmeta2_mode
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
        print "playbook_cmd is", playbook_cmd
        
        print "running Ansible playbook..."
        os.system(playbook_cmd)
        print "Sleeping... zzzz"
        time.sleep(30)
        
