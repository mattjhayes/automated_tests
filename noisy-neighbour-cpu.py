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
Run noisy neighbour CPU test agains filt performance
to see if high CPU on another guest can cause filter
performance to change
"""
import datetime
import time
import os
from os.path import expanduser
import sys

version = "0.1.0"
#*** How many times to run the set of tests:
repeats = 5
#*** Types of tests to run:
tests = ["controller-cpu-load", "no-controller-cpu-load"]

#*** Directory base path to write results to:
home_dir = expanduser("~")
results_dir = os.path.join(home_dir, "results/noisy-neighbour-tests/")
print "results_dir is", results_dir

#*** Ansible Playbook to use:
playbook = os.path.join(home_dir, "automated_tests/noisy-neighbour-template.yml")

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
        playbook_cmd = "ansible-playbook " + playbook + " --extra-vars "
        playbook_cmd += "\"algorithm=make-good"
        playbook_cmd += " results_dir=" + test_dir + "/"
        if test == "controller-cpu-load":
            playbook_cmd += " cpu_load=true" + "\""
        else:
            playbook_cmd += " cpu_load=false" + "\""
        print "playbook_cmd is", playbook_cmd
        
        print "running Ansible playbook..."
        os.system(playbook_cmd)
        print "Sleeping... zzzz"
        time.sleep(2)
        
