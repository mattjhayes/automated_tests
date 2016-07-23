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

./cp_timely_load_post_processing.py
simpleswitch
~/results/timeliness/controlplane/20160516202631/simpleswitch/20160516203449
50
00:00:00:00:12:34

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
FILENAME_TCPDUMP = 'lg1.example.com-tcpdump_cp_timely.txt'

#*** Files to write control plane response time to:
FILENAME_TT_SNOOP = 'post_process_control_plane_snoop_time_delta.csv'
FILENAME_TT_TRAFFIC = 'post_process_control_plane_traffic_time_delta.csv'

#*** Packet telemetry parameters:
FILENAME_INPUT_INITIAL_CT_PKTS = 'ct1.example.com_interface_eth2_initial.txt'
FILENAME_INPUT_FINAL_CT_PKTS = 'ct1.example.com_interface_eth2_final.txt'
FILENAME_RESULT_CT_PKTS = 'post_process_controller_pkts.csv'
FILENAME_INPUT_INITIAL_SV_PKTS = 'sv1.example.com_interface_mac0_initial.txt'
FILENAME_INPUT_FINAL_SV_PKTS = 'sv1.example.com_interface_mac0_final.txt'
FILENAME_RESULT_SV_PKTS = 'post_process_server_pkts.csv'

#*** Control plane response time to use if result not found:
ERROR_TIME = 99

#*** Files to write errors to:
FILENAME_ERROR_SNOOP = 'error_openvswitch_snoop.txt'
FILENAME_ERROR_TRAFFIC = 'error_traffic_capture.txt'

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

    #*** TRAFFIC CALCS, based off tcp dump last timestamp for crafted pkt:
    (traffic_last_time, matched_crafted_packets) = get_traffic_last_time()
    if crafted_pkt_send_time and traffic_last_time:
        delta = traffic_last_time - crafted_pkt_send_time
        result = TEST_TYPE + ',' + str(LOAD_RATE) + ',' \
                                 + str(delta.total_seconds()) + ',' \
                                 + str(matched_crafted_packets)
        #*** Write result to file:
        write_result(FILENAME_TT_TRAFFIC, result)
    else:
        #*** Uh-oh, something must have gone wrong... Lets write
        #*** something to file for triage later:
        write_error(FILENAME_ERROR_TRAFFIC, "Error: crafted_pkt_send_time=" + \
                    str(crafted_pkt_send_time) + \
                    " traffic_last_time=" + \
                    str(traffic_last_time))

    #*** Controller interface packet calcs:
    ct1_initial_pkts_in = 0
    ct1_initial_pkts_out = 0
    ct1_final_pkts_in = 0
    ct1_final_pkts_out = 0
    (ct1_initial_pkts_in, ct1_initial_pkts_out) = get_pkts(FILENAME_INPUT_INITIAL_CT_PKTS)
    (ct1_final_pkts_in, ct1_final_pkts_out) = get_pkts(FILENAME_INPUT_FINAL_CT_PKTS)
    if ct1_initial_pkts_in and ct1_final_pkts_in:
        ct1_pkts_in = ct1_final_pkts_in - ct1_initial_pkts_in
    else:
        ct1_pkts_in = 0
    if ct1_initial_pkts_out and ct1_final_pkts_out:
        ct1_pkts_out = ct1_final_pkts_out - ct1_initial_pkts_out
    else:
        ct1_pkts_out = 0
    #*** Write result to file:
    result = TEST_TYPE + ',' + str(LOAD_RATE) + ',' \
                                 + str(ct1_pkts_in) + ',' \
                                 + str(ct1_pkts_out)
    write_result(FILENAME_RESULT_CT_PKTS, result)

    #*** Server interface packet calcs:
    sv1_initial_pkts_in = 0
    sv1_initial_pkts_out = 0
    sv1_final_pkts_in = 0
    sv1_final_pkts_out = 0
    (sv1_initial_pkts_in, sv1_initial_pkts_out) = get_pkts(FILENAME_INPUT_INITIAL_SV_PKTS)
    (sv1_final_pkts_in, sv1_final_pkts_out) = get_pkts(FILENAME_INPUT_FINAL_SV_PKTS)
    if sv1_initial_pkts_in and sv1_final_pkts_in:
        sv1_pkts_in = sv1_final_pkts_in - sv1_initial_pkts_in
    else:
        sv1_pkts_in = 0
    if sv1_initial_pkts_out and sv1_final_pkts_out:
        sv1_pkts_out = sv1_final_pkts_out - sv1_initial_pkts_out
    else:
        sv1_pkts_out = 0
    #*** Write result to file:
    result = TEST_TYPE + ',' + str(LOAD_RATE) + ',' \
                                 + str(sv1_pkts_in) + ',' \
                                 + str(sv1_pkts_out)
    write_result(FILENAME_RESULT_SV_PKTS, result)

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

def get_traffic_last_time():
    """
    return the timestamp of the last line in the tcpdump file
    """
    traffic_last_time = 0
    matched_crafted_packets = 0
    filename = os.path.join(TEST_DIR, FILENAME_TCPDUMP)
    with open(filename, 'r') as f:
        for line in f.readlines():
            #*** Call function to check the line to see if it is
            #***  a matching packet
            #***  and if so, return time in UTC timezone:
            packet_time = check_tcpdump_line(line)
            if packet_time:
                traffic_last_time = packet_time
                matched_crafted_packets += 1
    return (traffic_last_time, matched_crafted_packets)

def check_tcpdump_line(tcpdump_line):
    """
    Passed a line from a tcpdump file and determine if it is
    a packet sent to the crafted mac. If it is then
    return the time in usable format
    (datetime object with correct timezone).
    """
    #*** Extract date/time from the line:

    #1464863476.514938 08:00:27:2a:d6:dd > 00:00:00:00:12:34, ethertype IPv4 (0x0800), length 60: 10.1.0.2.1234 > 10.1.2.7.5678: Flags [S], seq 0, win 8192, length 0


    print("tcpdump_line is ", tcpdump_line)

    tcpdump_match = \
                re.match(r"^(\S+)\s([^\s]+)\s+\>\s+([^\,]+).*", tcpdump_line)
    if tcpdump_match:
        print("tcpdump_match is ", tcpdump_match.group(1), tcpdump_match.group(2), tcpdump_match.group(3))
        if str(tcpdump_match.group(3)) == CRAFTED_MAC:
            print("matched dst crafted MAC, returning time=", tcpdump_match.group(1))
            #*** Convert timestamp:
            pkt_time = datetime.fromtimestamp(float(tcpdump_match.group(1)))
            pkt_time_tz = LOCAL_TZ.localize(pkt_time)
            return pkt_time_tz
        else:
            print("Dst MAC ", tcpdump_match.group(3), " not equal to crafted MAC, returning 0")
            return 0
    print("no match, returning 0")
    return 0

def get_pkts(filename):
    """
    Read in a Linux interface text output and return the RX and TX
    packet counts. Example input:

    mac0    Link encap:Ethernet  HWaddr 00:00:00:00:12:34  
            inet addr:10.1.2.7  Bcast:10.1.3.255  Mask:255.255.252.0
            inet6 addr: fe80::2ce7:79ff:feb8:93b0/64 Scope:Link
            UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
            RX packets:804 errors:0 dropped:0 overruns:0 frame:0
            TX packets:418 errors:0 dropped:0 overruns:0 carrier:0
            collisions:0 txqueuelen:0 
            RX bytes:48240 (48.2 KB)  TX bytes:22668 (22.6 KB)

    Result would be tuple of 804, 418
    """
    pkts_in = 0
    pkts_out = 0
    filename = os.path.join(TEST_DIR, filename)
    with open(filename, 'r') as f:
        for line in f.readlines():
            #*** Try RX and TX matches:
            rx_pkt_match = \
                re.search(r"^\s+RX\spackets\:(\d+).*", line)
            if rx_pkt_match:
                pkts_in = rx_pkt_match.group(1)
            tx_pkt_match = \
                re.search(r"^\s+TX\spackets\:(\d+).*", line)
            if tx_pkt_match:
                pkts_out = tx_pkt_match.group(1)
    return int(pkts_in), int(pkts_out)

def write_result(filename, value):
    """
    Write a result value to a file (overwrites)
    """
    print("Writing result", value, "to file", filename)
    result_filename = os.path.join(TEST_DIR, filename)
    with open(result_filename, 'w') as f:
        print(value, file=f)

def write_error(error_filename, parameter):
    """
    Append an error message to error file
    """
    print(parameter)
    error_filename = os.path.join(TEST_DIR, error_filename)
    with open(error_filename, 'a') as f:
        print(parameter, file=f)

if __name__ == '__main__':
    main()


