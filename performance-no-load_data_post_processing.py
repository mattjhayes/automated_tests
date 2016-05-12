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
Data Post-Processing for performance (no load) experiements prior to
ingestion by R

Pass it full path to directory that contains test result
files to post-process

Example:

./performance-no-load_data_post_processing.py ~/results/performance-no-load/20160508101013/nmeta2-active \
     /20160414211230/nmeta2-constrained-bw-iperf/20160414211648

This script is called by the Ansible YAML template, so does not need to
be run manually.

"""
#*** For writing to file:
from __future__ import print_function

import os, sys

#*** Regular Expressions import:
import re

#*** Constants for filenames to process:
FILENAME_HPING3 = 'pc1.example.com-hping3_output.txt'

#*** File to write traffic treatment time to:
FILENAME_TT = 'post_process_hping3.csv'

#*** File to write errors to:
FILENAME_ERROR = 'error.txt'

#*** Must have 1 parameter passed to it (first parameter is script)
assert len(sys.argv) == 2

#*** Get parameters from command line
TEST_DIR = sys.argv[1]

def main():
    """
    Main function
    """
    filename = os.path.join(TEST_DIR, FILENAME_HPING3)
    with open(filename, 'r') as f:
        for line in f.readlines():
            hping3_result = check_hping3_line(line)
            if hping3_result:
                write_result(FILENAME_TT, hping3_result)

def check_hping3_line(hping3_line):
    """
    Passed a line from the hping3 output file and return the
    result if it exists, otherwise 0.
    """
    #*** Extract hping3 time from the line:
    #*** Example: len=46 ip=10.1.0.2 ttl=64 DF id=36185 sport=0 flags=RA seq=6 win=0 rtt=9.1 ms
    print ("checking match against", hping3_line)
    hping3_match = \
                re.search(r"rtt=(\S+)", hping3_line)
    if hping3_match:
        print ("matched", hping3_match.groups()[0])
        result = hping3_match.groups()[0]
        return result
    else:
        return 0

def write_result(filename, value):
    """
    Write a result value to a file (overwrites)
    """
    print("Writing result", value, "to file", filename)
    result_filename = os.path.join(TEST_DIR, filename)
    with open(result_filename, 'a') as f:
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


