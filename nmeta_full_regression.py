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
Run full suite of nmeta regression tests
in an easy automated manner to make regression testing
nmeta updates a breeze...

Designed to fails as soon as there is an issue to avoid
unnecessary time waiting to be advised of regression issue that
needs fixing

Provides quantitative (performance) and qualitative (pass test) data
"""
import datetime
import os
import time
from os.path import expanduser
import sys

#*** Logging imports:
import logging
import logging.handlers
import coloredlogs

#*** Filename for results to be written to:
LOGGING_FILENAME = 'test_results.txt'
LOGGING_FILE_LEVEL = logging.INFO
LOGGING_FILE_FORMAT = "%(asctime)s %(levelname)s: " \
                            "%(funcName)s: %(message)s"

#*** Parameters for capture of environment configuration:
ENVIRONMENT_PLAYBOOK = 'nmeta-full-regression-environment-template.yml'

#*** Parameters for regression of Static classification:
STATIC_REPEATS = 1
STATIC_TESTS = ["constrained-bw-tcp1234", "constrained-bw-tcp5555"]
STATIC_DURATION = 10
STATIC_PLAYBOOK = 'nmeta-full-regression-static-template.yml'
STATIC_PAUSE_SWITCH2CONTROLLER = 30
STATIC_SLEEP = 30
STATIC_TEST_FILES = ["pc1.example.com-1234-iperf_result.txt",
                    "pc1.example.com-5555-iperf_result.txt"]
STATIC_THRESHOLD_CONSTRAINED = 200000
STATIC_THRESHOLD_UNCONSTRAINED = 1000000

#*** Parameters for regression of Identity classification:
IDENTITY_REPEATS = 1
IDENTITY_TESTS = ["lg1-constrained-bw", "pc1-constrained-bw"]
IDENTITY_DURATION = 10
IDENTITY_PLAYBOOK = 'nmeta-full-regression-identity-template.yml'
IDENTITY_TCP_PORT = 5555
IDENTITY_PAUSE1_SWITCH2CONTROLLER = 10
IDENTITY_PAUSE2_LLDPLEARN = 30
IDENTITY_PAUSE3_INTERTEST = 6
IDENTITY_SLEEP = 30
IDENTITY_TEST_FILES = ["lg1.example.com-iperf_result.txt",
                    "pc1.example.com-iperf_result.txt"]
IDENTITY_THRESHOLD_CONSTRAINED = 200000
IDENTITY_THRESHOLD_UNCONSTRAINED = 1000000

#*** Parameters for regression of Statistical classification:
STATISTICAL_REPEATS = 1
STATISTICAL_TESTS = ["constrained-bw-iperf", "unconstrained-bw-iperf"]
STATISTICAL_DURATION = 10
STATISTICAL_PLAYBOOK = 'nmeta-full-regression-statistical-template.yml'
STATISTICAL_TCP_PORT = 5555
STATISTICAL_PAUSE_SWITCH2CONTROLLER = 10
STATISTICAL_SLEEP = 30
STATISTICAL_TEST_FILES = ["pc1.example.com-iperf_result.txt",]
STATISTICAL_THRESHOLD_CONSTRAINED = 280000
STATISTICAL_THRESHOLD_UNCONSTRAINED = 1000000

#*** Parameters for analysis of nmeta syslog events:
LOGROTATE_PLAYBOOK = 'nmeta-full-regression-logrotate-template.yml'
LOGCHECK_PLAYBOOK = 'nmeta-full-regression-logcheck-template.yml'

def main(argv):
    """
    Main function of nmeta regression tests.
    Sets up logging, creates the timestamped directory
    and runs functions for the various regression test types
    """
    version = "0.1.1"

    #*** Set up logging:
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    coloredlogs.install(level="DEBUG",
                logger=logger,
                fmt="%(asctime)s.%(msecs)03d %(name)s[%(process)d] " \
           "%(funcName)s %(levelname)s %(message)s", datefmt='%H:%M:%S')
    logger.info("Running full regression test of nmeta")

    #*** Timestamp for results root directory:
    timenow = datetime.datetime.now()
    timestamp = timenow.strftime("%Y%m%d%H%M%S")
    logger.info("root results timestamp is %s", timestamp)

    #*** Directory base path to write results to:
    home_dir = expanduser("~")
    results_dir = os.path.join(home_dir,
                                   "results/regression/nmeta-full/")
    #*** Ansible Playbook directory:
    playbook_dir = os.path.join(home_dir, 'automated_tests')

    #*** Create root directory for results:
    os.chdir(results_dir)
    logger.debug("creating subdirectory %s", timestamp)
    os.mkdir(timestamp)
    basedir = os.path.join(results_dir, timestamp)
    logger.info("base directory is %s", basedir)

    #*** Set up logging to file in the root dir for these results:
    logging_file = os.path.join(basedir, LOGGING_FILENAME)
    logging_fh = logging.FileHandler(logging_file)
    logging_fh.setLevel(LOGGING_FILE_LEVEL)
    formatter = logging.Formatter(LOGGING_FILE_FORMAT)
    logging_fh.setFormatter(formatter)
    logger.addHandler(logging_fh)

    #*** Capture environment settings:
    #regression_environment(logger, basedir, playbook_dir)

    #*** Run static regression testing:
    regression_static(logger, basedir, playbook_dir)

    #*** Run identity regression testing:
    regression_identity(logger, basedir, playbook_dir)

    #*** Run statistical regression testing:
    regression_statistical(logger, basedir, playbook_dir)

    #*** And we're done!:
    logger.info("All testing finished, that's a PASS!")
    logger.info("See test report at %s/%s", basedir, LOGGING_FILENAME)

def regression_environment(logger, basedir, playbook_dir):
    """
    Capture details of the environment including info
    on the nmeta build
    """
    playbook = os.path.join(playbook_dir, ENVIRONMENT_PLAYBOOK)
    logger.debug("playbook is %s", playbook)
    playbook_cmd = "ansible-playbook " + playbook
    playbook_cmd += " --extra-vars "
    playbook_cmd += "\"results_dir=" + basedir + "/"
    playbook_cmd += "\""
    logger.debug("playbook_cmd=%s", playbook_cmd)
    logger.info("running Ansible playbook...")
    os.system(playbook_cmd)

def regression_static(logger, basedir, playbook_dir):
    """
    Nmeta static classification regression testing
    """
    logger.info("running static regression testing")
    subdir = 'static'
    #*** Create subdirectory to write results to:
    os.chdir(basedir)
    os.mkdir(subdir)
    test_basedir = os.path.join(basedir, subdir)
    playbook = os.path.join(playbook_dir, STATIC_PLAYBOOK)
    logger.debug("playbook is %s", playbook)
    #*** Run tests
    for i in range(STATIC_REPEATS):
        for test in STATIC_TESTS:
            #*** Timestamp for specific test subdirectory:
            timenow = datetime.datetime.now()
            testdir_timestamp = timenow.strftime("%Y%m%d%H%M%S")
            logger.info("running test=%s", test)
            test_dir = os.path.join(test_basedir, test,
                                                    testdir_timestamp)
            if test == "constrained-bw-tcp1234":
                policy_name = "main_policy_regression_static.yaml"
            elif test == "constrained-bw-tcp5555":
                policy_name = "main_policy_regression_static_2.yaml"
            else:
                print "ERROR: unknown static test type", test
                sys.exit()
            playbook_cmd = "ansible-playbook " + playbook
            playbook_cmd += " --extra-vars "
            playbook_cmd += "\"duration=" + str(STATIC_DURATION)
            playbook_cmd += " results_dir=" + test_dir + "/"
            playbook_cmd += " policy_name=" + policy_name
            playbook_cmd += " pause1=" + \
                                    str(STATIC_PAUSE_SWITCH2CONTROLLER)
            playbook_cmd += "\""
            logger.debug("playbook_cmd=%s", playbook_cmd)
            logger.info("running Ansible playbook...")
            os.system(playbook_cmd)

            #*** Analyse static regression results:
            logger.debug("Reading results in directory %s", test_dir)
            results = {}
            for filename in STATIC_TEST_FILES:
                results[filename] = get_iperf_bw(test_dir, filename)

            #*** Validate that the results are as expected:
            if test == STATIC_TESTS[0]:
                constrained = results[STATIC_TEST_FILES[0]]
                unconstrained = results[STATIC_TEST_FILES[1]]
            elif test == STATIC_TESTS[1]:
                constrained = results[STATIC_TEST_FILES[1]]
                unconstrained = results[STATIC_TEST_FILES[0]]
            else:
                #*** Unknown error condition:
                logger.critical("UNKNOWN TEST TYPE. test=%s", test)
                sys.exit("Please fix this test code. Exiting...")
            logger.info("validating bw constrained=%s unconstrained=%s",
                                             constrained, unconstrained)
            assert constrained < STATIC_THRESHOLD_CONSTRAINED
            assert unconstrained > STATIC_THRESHOLD_UNCONSTRAINED
            logger.info("STATIC TC TEST PASSED. test=%s", test)
            logger.info("bandwidth constrained=%s unconstrained=%s",
                                constrained, unconstrained)
            logger.info("Sleeping... zzzz")
            time.sleep(STATIC_SLEEP)

def regression_identity(logger, basedir, playbook_dir):
    """
    Nmeta identity classification regression testing
    """
    logger.info("running identity regression testing")
    subdir = 'identity'
    #*** Create subdirectory to write results to:
    os.chdir(basedir)
    os.mkdir(subdir)
    test_basedir = os.path.join(basedir, subdir)
    playbook = os.path.join(playbook_dir, IDENTITY_PLAYBOOK)
    logger.debug("playbook is %s", playbook)
    #*** Run tests
    for i in range(IDENTITY_REPEATS):
        for test in IDENTITY_TESTS:
            #*** Timestamp for specific test subdirectory:
            timenow = datetime.datetime.now()
            testdir_timestamp = timenow.strftime("%Y%m%d%H%M%S")
            logger.info("running test=%s", test)
            test_dir = os.path.join(test_basedir, test,
                                                    testdir_timestamp)
            if test == "lg1-constrained-bw":
                policy_name = "main_policy_regression_identity.yaml"
            elif test == "pc1-constrained-bw":
                policy_name = "main_policy_regression_identity_2.yaml"
            else:
                print "ERROR: unknown identity test type", test
                sys.exit()
            playbook_cmd = "ansible-playbook " + playbook
            playbook_cmd += " --extra-vars "
            playbook_cmd += "\"duration=" + str(IDENTITY_DURATION)
            playbook_cmd += " results_dir=" + test_dir + "/"
            playbook_cmd += " policy_name=" + policy_name
            playbook_cmd += " tcp_port=" + str(IDENTITY_TCP_PORT)
            playbook_cmd += " pause1=" + \
                                  str(IDENTITY_PAUSE1_SWITCH2CONTROLLER)
            playbook_cmd += " pause2=" + \
                                    str(IDENTITY_PAUSE2_LLDPLEARN)
            playbook_cmd += " pause3=" + \
                                    str(IDENTITY_PAUSE3_INTERTEST)
            playbook_cmd += "\""
            logger.debug("playbook_cmd=%s", playbook_cmd)
            logger.info("running Ansible playbook...")
            os.system(playbook_cmd)

            #*** Analyse identity regression results:
            logger.debug("Reading results in directory %s", test_dir)
            results = {}
            for filename in IDENTITY_TEST_FILES:
                results[filename] = get_iperf_bw(test_dir, filename)

            #*** Validate that the results are as expected:
            if test == IDENTITY_TESTS[0]:
                constrained = results[IDENTITY_TEST_FILES[0]]
                unconstrained = results[IDENTITY_TEST_FILES[1]]
            elif test == IDENTITY_TESTS[1]:
                constrained = results[IDENTITY_TEST_FILES[1]]
                unconstrained = results[IDENTITY_TEST_FILES[0]]
            else:
                #*** Unknown error condition:
                logger.critical("UNKNOWN TEST TYPE. test=%s", test)
                sys.exit("Please fix this test code. Exiting...")
            logger.info("validating bw constrained=%s unconstrained=%s",
                                             constrained, unconstrained)
            assert constrained < IDENTITY_THRESHOLD_CONSTRAINED
            assert unconstrained > IDENTITY_THRESHOLD_UNCONSTRAINED
            logger.info("IDENTITY TC TEST PASSED. test=%s", test)
            logger.info("bandwidth constrained=%s unconstrained=%s",
                                constrained, unconstrained)

            logger.info("Sleeping... zzzz")
            time.sleep(IDENTITY_SLEEP)

def regression_statistical(logger, basedir, playbook_dir):
    """
    Nmeta statistical classification regression testing
    """
    logger.info("running statistical regression testing")
    subdir = 'statistical'
    #*** Create subdirectory to write results to:
    os.chdir(basedir)
    os.mkdir(subdir)
    test_basedir = os.path.join(basedir, subdir)
    playbook = os.path.join(playbook_dir, STATISTICAL_PLAYBOOK)
    logger.debug("playbook is %s", playbook)
    #*** Run tests
    for i in range(STATISTICAL_REPEATS):
        for test in STATISTICAL_TESTS:
            #*** Timestamp for specific test subdirectory:
            timenow = datetime.datetime.now()
            testdir_timestamp = timenow.strftime("%Y%m%d%H%M%S")
            logger.info("running test=%s", test)
            test_dir = os.path.join(test_basedir, test,
                                                    testdir_timestamp)
            rotate_log(logger, playbook_dir)
            if test == "constrained-bw-iperf":
                policy_name = "main_policy_regression_statistical.yaml"
            elif test == "unconstrained-bw-iperf":
                policy_name = \
                       "main_policy_regression_statistical_control.yaml"
            else:
                print "ERROR: unknown statistical test type", test
                sys.exit()
            playbook_cmd = "ansible-playbook " + playbook
            playbook_cmd += " --extra-vars "
            playbook_cmd += "\"duration=" + str(STATISTICAL_DURATION)
            playbook_cmd += " results_dir=" + test_dir + "/"
            playbook_cmd += " policy_name=" + policy_name
            playbook_cmd += " tcp_port=" + str(STATISTICAL_TCP_PORT)
            playbook_cmd += " pause1=" + \
                               str(STATISTICAL_PAUSE_SWITCH2CONTROLLER)
            playbook_cmd += "\""
            logger.debug("playbook_cmd=%s", playbook_cmd)
            logger.info("running Ansible playbook...")
            os.system(playbook_cmd)

            #logger.error("THIS IS A TEST...")

            #*** Analyse statistical regression results:
            logger.debug("Reading results in directory %s", test_dir)
            results = {}
            for filename in STATISTICAL_TEST_FILES:
                results[filename] = get_iperf_bw(test_dir, filename)

            #*** Validate that the results are as expected:
            if test == STATISTICAL_TESTS[0]:
                constrained = results[STATISTICAL_TEST_FILES[0]]
                logger.info("validating statistical bw constrained=%s",
                                                            constrained)
                assert constrained < STATISTICAL_THRESHOLD_CONSTRAINED
            elif test == STATISTICAL_TESTS[1]:
                unconstrained = results[STATISTICAL_TEST_FILES[0]]
                logger.info("validating statistical bw unconstrained=%s"
                                                        , unconstrained)
                assert unconstrained > \
                                     STATISTICAL_THRESHOLD_UNCONSTRAINED
            else:
                #*** Unknown error condition:
                logger.critical("UNKNOWN TEST TYPE. test=%s", test)
                sys.exit("Please fix this test code. Exiting...")

            logger.info("STATISTICAL TC TEST PASSED. test=%s", test)

            #*** Check for any logs that are CRITICAL or ERROR:
            check_log(logger, playbook_dir, test_dir)

            logger.info("Sleeping... zzzz")
            time.sleep(STATISTICAL_SLEEP)

def get_iperf_bw(test_dir, filename):
    """
    Passed the directory and filename of an Iperf result
    file and return the reported bandwidth or exit if error
    """
    filename_full = os.path.join(test_dir, filename)
    with open(filename_full) as filehandle:
        data = filehandle.read()
        data = data.split(",")
        #*** The result is position 8 and remove trailing newline:
        return int(str(data[8]).rstrip())

def rotate_log(logger, playbook_dir):
    """
    Run an Ansible playbook to rotate the nmeta log
    so that it is fresh for analysis post test
    """
    logger.info("Rotating nmeta syslog output for freshness")
    playbook = os.path.join(playbook_dir, LOGROTATE_PLAYBOOK)
    logger.debug("playbook is %s", playbook)
    playbook_cmd = "ansible-playbook " + playbook
    logger.debug("playbook_cmd=%s", playbook_cmd)
    logger.info("running Ansible playbook...")
    os.system(playbook_cmd)

def check_log(logger, playbook_dir, test_dir):
    """
    Check the nmeta log file to see if it has any log events that
    should cause the test to be failed so that code can be fixed
    """
    logger.info("Checking nmeta syslog for error or critical messages")
    playbook = os.path.join(playbook_dir, LOGCHECK_PLAYBOOK)
    logger.debug("playbook is %s", playbook)
    playbook_cmd = "ansible-playbook " + playbook
    playbook_cmd += " --extra-vars "
    playbook_cmd += "\"results_dir=" + test_dir + "/"
    playbook_cmd += "\""
    logger.debug("playbook_cmd=%s", playbook_cmd)
    logger.info("running Ansible playbook...")
    os.system(playbook_cmd)

    #*** TBD - check for presence of file:

#with file('bla.txt') as input:
#  for count, line in enumerate(input):
#    if re.search('foo bar', line):
#      print line

if __name__ == "__main__":
    #*** Run the main function with command line
    #***  arguments from position 1
    main(sys.argv[1:])
