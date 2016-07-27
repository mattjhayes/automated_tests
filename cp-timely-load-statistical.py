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
repeats = 12

#*** Types of tests to run:
#***  Note: don't do nmeta as it doesn't do MAC learning in switch
tests = ["nmeta", "nmeta2-active", "nmeta2-passive", "simpleswitch"]

#*** Directory base path to write results to:
home_dir = expanduser("~")
results_dir = os.path.join(home_dir,
                                "results/timeliness/controlplane/")


#*** Server parameters for extra ip/mac:
svr_int = 'eth1'
svr_crafted_mac = '00:00:00:00:12:34'
svr_crafted_ip = '10.1.2.7'
svr_masklength = '22'

#*** Parameters for repetition of tests with different filt rate:
test_load_initial_rate = 10
test_load_rate_increment = 20
test_load_max_rate = 250

#*** Parameters for filt new flow rate load test:
target_ip = "10.1.0.7"
target_mac = "08:00:27:40:e4:4c"
interface = "eth1"
flow_inc = "5"
incr_interval = "20"
proto = "6"
dport = "12345"
algorithm = "make-good"

#*** Ansible Playbooks to use:
playbook = os.path.join(home_dir, \
                    "automated_tests/cp-timely-load-template.yml")
playbook_svr = os.path.join(home_dir, \
                    "automated_tests/server-extra-ip-and-mac.yml")
#*** TBD:
#playbook_warmup = os.path.join(home_dir, \
#            "automated_tests/nfps-load-tests-template-warmup.yml")

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

setup_server_nic = raw_input("Set up server NIC? (y, otherwise no): ")
print "setup_server_nic is", setup_server_nic
if setup_server_nic == 'y':
    #*** Set extra ip and mac on server:
    print "running Ansible playbook to set up server extra ip and mac..."
    playbook_svr_cmd = "ansible-playbook " + playbook_svr + " --extra-vars "
    playbook_svr_cmd += "\"interface=" + svr_int
    playbook_svr_cmd += " mac=" + svr_crafted_mac
    playbook_svr_cmd += " ip=" + svr_crafted_ip
    playbook_svr_cmd += " masklength=" + svr_masklength
    playbook_svr_cmd += "\""
    print "playbook_svr_cmd is", playbook_svr_cmd
    os.system(playbook_svr_cmd)

#*** Run tests:
for i in range(repeats):
    test_load_rate = test_load_initial_rate
    while test_load_rate <= test_load_max_rate:
        for test in tests:
            print "======================================"
            print "running test", test, "at NFPS", test_load_rate, \
                            "test suite iteration", i+1, \
                             "of", repeats
            test_dir = os.path.join(test_basedir, test)
            #*** Rotate Ansible log:
            if os.path.isfile("/tmp/ansible.log"):
                os.rename("/tmp/ansible.log", "/tmp/ansible.log.old")
                os.mknod("/tmp/ansible.log")
            #*** Set test parameters:
            if test == "nmeta":
                start_nmeta = "true"
                start_nmeta2 = "false"
                nmeta2_mode = "none"
                start_simple_switch = "false"
                #*** TBD, make statistical, is it bug?
                policy_name = "main_policy_regression_static.yaml"
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
            elif test == "nosdn":
                start_nmeta = "false"
                start_nmeta2 = "false"
                nmeta2_mode = "none"
                start_simple_switch = "false"
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
            playbook_cmd += " max_rate=" + str(test_load_rate + 10)
            playbook_cmd += " flow_inc=" + str(test_load_rate_increment)
            playbook_cmd += " incr_interval=" + incr_interval
            playbook_cmd += " proto=" + proto
            playbook_cmd += " dport=" + dport
            playbook_cmd += " algorithm=" + algorithm
            playbook_cmd += " policy_name=" + policy_name
            playbook_cmd += " crafted_mac=" + svr_crafted_mac
            playbook_cmd += " crafted_ip=" + svr_crafted_ip
            playbook_cmd += "\""
            print "playbook_cmd is", playbook_cmd

            print "running Ansible playbook..."
            os.system(playbook_cmd)

            #*** Retrieve Ansible log:
            timenow = datetime.datetime.now()
            timestamp_ansible = timenow.strftime("%Y%m%d%H%M%S")
            dest_filename = timestamp_ansible + "-finished-ansible.log"
            ansible_log_dst = os.path.join(test_dir, dest_filename)
            os.rename("/tmp/ansible.log", ansible_log_dst)
            os.mknod("/tmp/ansible.log")
            
            print "Sleeping... zzzz"
            time.sleep(10)
        #*** Increment load rate:
        test_load_rate = test_load_rate + test_load_rate_increment

