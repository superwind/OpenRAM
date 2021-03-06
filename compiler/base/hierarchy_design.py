# See LICENSE for licensing information.
#
#Copyright (c) 2016-2019 Regents of the University of California and The Board
#of Regents for the Oklahoma Agricultural and Mechanical College
#(acting for and on behalf of Oklahoma State University)
#All rights reserved.
#
import hierarchy_layout
import hierarchy_spice
import globals
import verify
import debug
import os
from globals import OPTS

total_drc_errors = 0 
total_lvs_errors = 0

class hierarchy_design(hierarchy_spice.spice, hierarchy_layout.layout):
    """
    Design Class for all modules to inherit the base features.
    Class consisting of a set of modules and instances of these modules
    """
    name_map = []

    def __init__(self, name):
        self.gds_file = OPTS.openram_tech + "gds_lib/" + name + ".gds"
        self.sp_file = OPTS.openram_tech + "sp_lib/" + name + ".sp"

        self.name = name
        hierarchy_spice.spice.__init__(self, name)
        hierarchy_layout.layout.__init__(self, name)
        

    def get_layout_pins(self,inst):
        """ Return a map of pin locations of the instance offset """
        # find the instance
        for i in self.insts:
            if i.name == inst.name:
                break
        else:
            debug.error("Couldn't find instance {0}".format(inst_name),-1)
        inst_map = inst.mod.pin_map
        return inst_map
        

    def DRC_LVS(self, final_verification=False, top_level=False):
        """Checks both DRC and LVS for a module"""
        
        # Final verification option does not allow nets to be connected by label.
        # Unit tests will check themselves.
        if OPTS.is_unit_test:
            return
        if not OPTS.check_lvsdrc:
            return
        # Do not run if disabled in options.
        if (OPTS.inline_lvsdrc or top_level):

            global total_drc_errors
            global total_lvs_errors
            tempspice = "{0}/{1}.sp".format(OPTS.openram_temp,self.name)
            tempgds = "{0}/{1}.gds".format(OPTS.openram_temp,self.name)
            self.sp_write(tempspice)
            self.gds_write(tempgds)

            num_drc_errors = verify.run_drc(self.name, tempgds, final_verification) 
            num_lvs_errors = verify.run_lvs(self.name, tempgds, tempspice, final_verification) 
            debug.check(num_drc_errors == 0,"DRC failed for {0} with {1} error(s)".format(self.name,num_drc_errors))
            debug.check(num_lvs_errors == 0,"LVS failed for {0} with {1} errors(s)".format(self.name,num_lvs_errors))
            total_drc_errors += num_drc_errors
            total_lvs_errors += num_lvs_errors

            os.remove(tempspice)
            os.remove(tempgds)

    def DRC(self, final_verification=False):
        """Checks DRC for a module"""
        # Unit tests will check themselves.
        # Do not run if disabled in options.

        if (not OPTS.is_unit_test and OPTS.check_lvsdrc and (OPTS.inline_lvsdrc or final_verification)):
            global total_drc_errors
            tempgds = "{0}/{1}.gds".format(OPTS.openram_temp,self.name)
            self.gds_write(tempgds)
            num_errors = verify.run_drc(self.name, tempgds, final_verification)  
            total_drc_errors += num_errors
            debug.check(num_errors == 0,"DRC failed for {0} with {1} error(s)".format(self.name,num_error))

            os.remove(tempgds)

    def LVS(self, final_verification=False):
        """Checks LVS for a module"""
        # Unit tests will check themselves.
        # Do not run if disabled in options.

        if (not OPTS.is_unit_test and OPTS.check_lvsdrc and (OPTS.inline_lvsdrc or final_verification)):
            global total_lvs_errors
            tempspice = "{0}/{1}.sp".format(OPTS.openram_temp,self.name)
            tempgds = "{0}/{1}.gds".format(OPTS.openram_temp,self.name)
            self.sp_write(tempspice)
            self.gds_write(tempgds)
            num_errors = verify.run_lvs(self.name, tempgds, tempspice, final_verification)
            total_lvs_errors += num_errors
            debug.check(num_errors == 0,"LVS failed for {0} with {1} error(s)".format(self.name,num_errors))
            os.remove(tempspice)
            os.remove(tempgds)

    def __str__(self):
        """ override print function output """
        pins = ",".join(self.pins)
        insts = ["    {}".format(x) for x in self.insts]
        objs = ["    {}".format(x) for x in self.objs]  
        s = "********** design {0} **********".format(self.name)
        s += "\n  pins ({0})={1}\n".format(len(self.pins), pins)
        s += "\n  objs ({0})=\n{1}\n".format(len(self.objs), "\n".join(objs))
        s += "\n  insts ({0})=\n{1}\n".format(len(self.insts), "\n".join(insts))
        return s

    def __repr__(self):
        """ override print function output """
        text="( design: " + self.name + " pins=" + str(self.pins) + " " + str(self.width) + "x" + str(self.height) + " )\n"
        for i in self.objs:
            text+=str(i)+",\n"
        for i in self.insts:
            text+=str(i)+",\n"
        return text
     
