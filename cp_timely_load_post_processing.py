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
Post-Processing for CP timely experiements prior to
ingestion by R

Pass it full path to directory that contains test result
files to post-process, as well as the target load level and crafted MAC

Example:

./cp_timely_load_post_processing.py simpleswitch ~/results/timeliness/controlplane/20160516202631/simpleswitch/20160516203449 50 00:00:00:00:12:34

This script is called by the Ansible YAML template, so does not need to
be run manually.

"""
#*** For writing to file:
from __future__ import print_function

import os, sys

#*** Time-related imports:
from datetime import datetime
import pytz
from tzlocal import get_localzone

#*** Regular Expressions import:
import re

#*** Get parameters from command line
#*** Must have 5 parameters passed to it (first parameter is script)
assert len(sys.argv) == 5
TEST_TYPE = sys.argv[1]
TEST_DIR = sys.argv[2]
LOAD_RATE = sys.argv[3]
CRAFTED_MAC = sys.argv[4]

#*** Constants for filenames to process:
FILENAME_CRAFTED_PKT_SEND = 'crafted_pkt_starttime.txt'
FILENAME_FLOWUPDATES = 'sw1.example.com-OF-snooping.txt'

#*** File to write control plane response time to:
FILENAME_TT = 'post_process_control_plane_time_delta.txt'

#*** Control plane response time to use if result not found:
ERROR_TIME = 99

#*** File to write errors to:
FILENAME_ERROR = 'error.txt'

#*** For finding flow entry that indicates MAC has been learnt (nmeta2):
FT_FWD = 5
FT_FWD_PRIORITY = 1

#*** Timezones (for conversions to UTC):
UTC = pytz.utc
LOCAL_TZ = get_localzone()




def main():
    """
    Main function
    """
    #*** Get the time for when the crafted packet was sent:
    crafted_pkt_send_time = get_crafted_pkt_send_time()

    #*** Get the time when forwarding was applied on the switch:
    forwarding_rule_time = get_forwarding_rule_time()

    #*** Calculate the delta between Iperf start and traffic treatment:
    if crafted_pkt_send_time and forwarding_rule_time:
        delta = forwarding_rule_time - crafted_pkt_send_time
        result = TEST_TYPE + ',' + str(LOAD_RATE) + ',' \
                                            + str(delta.total_seconds())
        #*** Write result to file:
        write_result(FILENAME_TT, result)
    else:
        #*** Uh-oh, something must have gone wrong... Lets write
        #*** something to file for triage later:
        write_error("Error: crafted_pkt_send_time=" + \
                    str(crafted_pkt_send_time) + \
                    " forwarding_rule_time=" + \
                    str(forwarding_rule_time))

def get_crafted_pkt_send_time():
    """
    Return the crafted packet send time, or 0 if error
    """
    crafted_pkt_st = 0
    #*** Read in the crafted_pkt start time:
    filename = os.path.join(TEST_DIR, FILENAME_CRAFTED_PKT_SEND)
    with open(filename, 'r') as f:
         crafted_pkt_st = f.readline()
    if crafted_pkt_st:
        crafted_pkt_st = datetime.fromtimestamp(float(crafted_pkt_st))
        crafted_pkt_st_tz = LOCAL_TZ.localize(crafted_pkt_st)
        print("Crafted packet was sent at", crafted_pkt_st_tz)
        return crafted_pkt_st_tz
    else:
        print("Error finding crafted packet send time")
        return 0

def get_forwarding_rule_time():
    """
    Return the time when treatment was applied on the switch,
    or 0 if error
    """
    forwarding_rule_time = 0
    #*** Read in the TC Flow Entry (Treatment) Install Time on Switch:
    filename = os.path.join(TEST_DIR, FILENAME_FLOWUPDATES)
    with open(filename, 'r') as f:
        for line in f.readlines():
            if not forwarding_rule_time:
                #*** Call function to check the line to see if it is
                #***  install of forwarding rule for specific MAC
                #***  and if so, return time in UTC timezone:
                forwarding_rule_time = check_snoop_line(line, UTC)
    if forwarding_rule_time:
        return forwarding_rule_time
    else:
        print("WARNING: failed to find a forwarding rule install entry")
        return 0

def check_snoop_line(snoop_line, timezone):
    """
    Passed a line from the OVS snooping file and determine if it is
    the forwarding rule being applied for the specific source MAC
    sent in the crafted packet. If forwarding rule install is
    found, return the time in usable format
    (datetime object with correct timezone).
    """
    #*** Extract date/time from the line:
    #*** Example line start: 2016-04-14 09:14:38.592: OFPT_FLOW_MOD...
    #*** date time is in group 1:
    of_snoop_match = \
                re.match(r"^(\d+\-\d+\-\d+\s+\d+\:\d+\:\d+\.\d+).*",
                snoop_line)
    if of_snoop_match:
        #*** Now see if line contains pattern for a treatment:
        if TEST_TYPE == 'nmeta2-active' or TEST_TYPE == 'nmeta2-passive':
            treatment_match = \
                re.search(r"table\:5\spriority\=1\,dl_dst\=00\:00\:00\:00\:12\:34",
                snoop_line)
        elif TEST_TYPE == 'simpleswitch':
            treatment_match = \
                re.search(r"dl_dst\=00\:00\:00\:00\:12\:34\sout\_port\:0\sactions\=\output\:1",
                snoop_line)
        else:
            print("Error, unknown test type ", TEST_TYPE)
            return 0
        if treatment_match:
            print("matched treatment on line ", snoop_line)
            tt_datetime = of_snoop_match.group(1)
            pattern = '%Y-%m-%d %H:%M:%S.%f'
            tt_datetime2 = datetime.strptime(tt_datetime, pattern)
            tt_datetime2_tz = timezone.localize(tt_datetime2)
            print("treatment_time_tz is ", tt_datetime2_tz)
            return tt_datetime2_tz
    return 0

def write_result(filename, value):
    """
    Write a result value to a file (overwrites)
    """
    print("Writing result", value, "to file", filename)
    result_filename = os.path.join(TEST_DIR, filename)
    with open(result_filename, 'w') as f:
        print(value, file=f)

def write_error(parameter):
    """
    Append an error message to error file
    """
    print(parameter)
    error_filename = os.path.join(TEST_DIR, FILENAME_ERROR)
    with open(error_filename, 'a') as f:
        print(parameter, file=f)

if __name__ == '__main__':
    main()


