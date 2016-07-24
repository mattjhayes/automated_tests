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
Run nmeta and nmeta2 statistical TC timeliness tests
"""
import datetime
import time
import os
from os.path import expanduser
import sys

version = "0.1.1"

#*** How many times to run the set of tests:
repeats = 30

#*** Types of tests to run:
tests = ["nmeta2-statistical-active", "nmeta2-statistical-passive"]

#*** Directory base path to write results to:
home_dir = expanduser("~")
results_dir = os.path.join(home_dir,
                                "results/timeliness/statistical/")

#*** Parameters for regression test:
duration="10"

#*** Ansible Playbook to use:
playbook = os.path.join(home_dir, \
                    "automated_tests/tc-timely-noload-statistical-template.yml")

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
start_nmeta="false"
start_nmeta2="false"

#*** Run tests
for i in range(repeats):
    for test in tests:
        print "running test", test, "test suite iteration", i+1, "of", \
                                                            repeats
        test_dir=os.path.join(test_basedir, test)
        #*** Rotate Ansible log:
        if os.path.isfile("/tmp/ansible.log"):
            os.rename("/tmp/ansible.log", "/tmp/ansible.log.old")
            os.mknod("/tmp/ansible.log")
        #*** Set up test-specific parameters:
        if test == "nmeta2-statistical-active":
            start_nmeta="false"
            start_nmeta2="true"
            policy_name="main_policy_regression_statistical.yaml"
        elif test == "nmeta2-statistical-passive":
            start_nmeta="false"
            start_nmeta2="true"
            policy_name="main_policy_regression_statistical_passive.yaml"
        elif test == "nmeta2-statistical-control":
            start_nmeta="false"
            start_nmeta2="true"
            policy_name="main_policy_regression_statistical_control.yaml"
        else:
            print "ERROR: unknown test type", test
            sys.exit()
        playbook_cmd = "ansible-playbook " + playbook + " --extra-vars "
        playbook_cmd += "\"start_nmeta=" + start_nmeta
        playbook_cmd += " start_nmeta2=" + start_nmeta2
        playbook_cmd += " duration=" + duration
        playbook_cmd += " results_dir=" + test_dir + "/"
        playbook_cmd += " policy_name=" + policy_name
        playbook_cmd += "\""
        print "playbook_cmd is", playbook_cmd
        
        print "running Ansible playbook..."
        os.system(playbook_cmd)

        #*** Retrieve Ansible log:
        timenow = datetime.datetime.now()
        timestamp_ansible = timenow.strftime("%Y%m%d%H%M%S")
        dest_filename = timestamp + "-finished-ansible.log"
        ansible_log_dst = os.path.join(test_dir, dest_filename)
        os.rename("/tmp/ansible.log", ansible_log_dst)
        os.mknod("/tmp/ansible.log")
            
        print "Sleeping... zzzz"
        time.sleep(30)
        
