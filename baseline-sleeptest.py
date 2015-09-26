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
Run sleep tests
"""
import datetime
import time
import os
from os.path import expanduser
import sys

version = "0.1.0"
#*** How many times to run the set of tests:
repeats = 3

#*** Directory base path to write results to:
home_dir = expanduser("~")
results_dir = os.path.join(home_dir, "results/sleeptests/")
print "results_dir is", results_dir

#*** Ansible Playbook to use:
playbook = os.path.join(home_dir, \
                     "automated_tests/baseline-sleeptest-template.yml")

#*** Timestamp for results root directory:
timenow = datetime.datetime.now()
timestamp = timenow.strftime("%Y%m%d%H%M%S")
print "timestamp is", timestamp

#*** Create root directory for results:
os.chdir(results_dir)
os.mkdir(timestamp)
test_dir = os.path.join(results_dir, timestamp)
print "test_dir is", test_dir

#*** Run tests
for i in range(repeats):
    print "running test"
    playbook_cmd = "ansible-playbook " + playbook + " --extra-vars "
    playbook_cmd += "\"results_dir=" + test_dir + "/\""
    print "playbook_cmd is", playbook_cmd
    print "running Ansible playbook..."
    os.system(playbook_cmd)
    print "Sleeping... zzzz"
    time.sleep(2)
        
