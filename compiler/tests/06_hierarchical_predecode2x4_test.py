#!/usr/bin/env python3
# See LICENSE for licensing information.
#
#Copyright (c) 2016-2019 Regents of the University of California and The Board
#of Regents for the Oklahoma Agricultural and Mechanical College
#(acting for and on behalf of Oklahoma State University)
#All rights reserved.
#
"""
Run a regression test on a hierarchical_predecode2x4.
"""

import unittest
from testutils import header,openram_test
import sys,os
sys.path.append(os.path.join(sys.path[0],".."))
import globals
from globals import OPTS
from sram_factory import factory
import debug

class hierarchical_predecode2x4_test(openram_test):

    def runTest(self):
        globals.init_openram("config_{0}".format(OPTS.tech_name))

        # checking hierarchical precode 2x4 for single port
        debug.info(1, "Testing sample for hierarchy_predecode2x4")
        a = factory.create(module_type="hierarchical_predecode2x4")
        self.local_check(a)

        # checking hierarchical precode 2x4 for multi-port
        OPTS.bitcell = "pbitcell"
        OPTS.num_rw_ports = 1
        OPTS.num_w_ports = 0
        OPTS.num_r_ports = 0
        
        debug.info(1, "Testing sample for hierarchy_predecode2x4 (multi-port case)")
        a = factory.create(module_type="hierarchical_predecode2x4")
        self.local_check(a)
        
        globals.end_openram()
        
# run the test from the command line
if __name__ == "__main__":
    (OPTS, args) = globals.parse_args()
    del sys.argv[1:]
    header(__file__, OPTS.tech_name)
    unittest.main()
