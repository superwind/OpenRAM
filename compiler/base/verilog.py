# See LICENSE for licensing information.
#
#Copyright (c) 2016-2019 Regents of the University of California and The Board
#of Regents for the Oklahoma Agricultural and Mechanical College
#(acting for and on behalf of Oklahoma State University)
#All rights reserved.
#
import debug

class verilog:
    """ 
    Create a behavioral Verilog file for simulation.
    This is inherited by the sram_base class.
    """
    def __init__(self):
        pass
        
    def verilog_write(self,verilog_name):
        """ Write a behavioral Verilog model. """
        self.vf = open(verilog_name, "w")

        self.vf.write("// OpenRAM SRAM model\n")
        self.vf.write("// Words: {0}\n".format(self.num_words))
        self.vf.write("// Word size: {0}\n\n".format(self.word_size))

        self.vf.write("module {0}(\n".format(self.name))
        for port in self.all_ports:
            if port in self.readwrite_ports:
                self.vf.write("// Port {0}: RW\n".format(port))
            elif port in self.read_ports:
                self.vf.write("// Port {0}: R\n".format(port))
            elif port in self.write_ports:
                self.vf.write("// Port {0}: W\n".format(port))
            if port in self.readwrite_ports:
                self.vf.write("    clk{0},csb{0},web{0},ADDR{0},DIN{0},DOUT{0}".format(port))
            elif port in self.write_ports:
                self.vf.write("    clk{0},csb{0},ADDR{0},DIN{0}".format(port))
            elif port in self.read_ports:
                self.vf.write("    clk{0},csb{0},ADDR{0},DOUT{0}".format(port))
            # Continue for every port on a new line
            if port != self.all_ports[-1]:
                self.vf.write(",\n")
        self.vf.write("\n  );\n\n")
        
        self.vf.write("  parameter DATA_WIDTH = {0} ;\n".format(self.word_size))
        self.vf.write("  parameter ADDR_WIDTH = {0} ;\n".format(self.addr_size))
        self.vf.write("  parameter RAM_DEPTH = 1 << ADDR_WIDTH;\n")
        self.vf.write("  // FIXME: This delay is arbitrary.\n")
        self.vf.write("  parameter DELAY = 3 ;\n")
        self.vf.write("\n")

        for port in self.all_ports:
            self.add_inputs_outputs(port)

        self.vf.write("\n")
            
        for port in self.all_ports:
            self.register_inputs(port)

        # This is the memory array itself
        self.vf.write("reg [DATA_WIDTH-1:0]    mem [0:RAM_DEPTH-1];\n")

        for port in self.all_ports:
            if port in self.write_ports:
                self.add_write_block(port)
            if port in self.read_ports:
                self.add_read_block(port)
                
        self.vf.write("\n")    
        self.vf.write("endmodule\n")
        self.vf.close()


    def register_inputs(self, port):
        """
        Register the control signal, address and data inputs.
        """
        self.add_regs(port)
        self.add_flops(port)
            
    def add_regs(self, port):
        """ 
        Create the input regs for the given port.
        """
        self.vf.write("  reg  csb{0}_reg;\n".format(port))
        if port in self.readwrite_ports:
            self.vf.write("  reg  web{0}_reg;\n".format(port))
        self.vf.write("  reg [ADDR_WIDTH-1:0]  ADDR{0}_reg;\n".format(port))
        if port in self.write_ports:
            self.vf.write("  reg [DATA_WIDTH-1:0]  DIN{0}_reg;\n".format(port))
        if port in self.read_ports:
            self.vf.write("  reg [DATA_WIDTH-1:0]  DOUT{0};\n".format(port))
            
    def add_flops(self, port):
        """
        Add the flop behavior logic for a port.
        """
        self.vf.write("\n")
        self.vf.write("  // All inputs are registers\n")
        self.vf.write("  always @(posedge clk{0})\n".format(port))
        self.vf.write("  begin\n")
        self.vf.write("    csb{0}_reg = csb{0};\n".format(port))
        if port in self.readwrite_ports:
            self.vf.write("    web{0}_reg = web{0};\n".format(port))
        self.vf.write("    ADDR{0}_reg = ADDR{0};\n".format(port))
        if port in self.write_ports:
            self.vf.write("    DIN{0}_reg = DIN{0};\n".format(port))
        if port in self.read_ports:
            self.vf.write("    DOUT{0} = {1}'bx;\n".format(port,self.word_size))
        if port in self.readwrite_ports:
            self.vf.write("    if ( !csb{0}_reg && web{0}_reg ) \n".format(port))
            self.vf.write("      $display($time,\" Reading %m ADDR{0}=%b DOUT{0}=%b\",ADDR{0}_reg,mem[ADDR{0}_reg]);\n".format(port))
        elif port in self.read_ports:
            self.vf.write("    if ( !csb{0}_reg ) \n".format(port))
            self.vf.write("      $display($time,\" Reading %m ADDR{0}=%b DOUT{0}=%b\",ADDR{0}_reg,mem[ADDR{0}_reg]);\n".format(port))
            
        if port in self.readwrite_ports:
            self.vf.write("    if ( !csb{0}_reg && !web{0}_reg )\n".format(port))
            self.vf.write("      $display($time,\" Writing %m ADDR{0}=%b DIN{0}=%b\",ADDR{0}_reg,DIN{0}_reg);\n".format(port))
        elif port in self.write_ports:
            self.vf.write("    if ( !csb{0}_reg )\n".format(port))
            self.vf.write("      $display($time,\" Writing %m ADDR{0}=%b DIN{0}=%b\",ADDR{0}_reg,DIN{0}_reg);\n".format(port))
        self.vf.write("  end\n\n")
            

    def add_inputs_outputs(self, port):
        """
        Add the module input and output declaration for a port.
        """
        self.vf.write("  input  clk{0}; // clock\n".format(port))
        self.vf.write("  input   csb{0}; // active low chip select\n".format(port))
        if port in self.readwrite_ports:
            self.vf.write("  input  web{0}; // active low write control\n".format(port))
        self.vf.write("  input [ADDR_WIDTH-1:0]  ADDR{0};\n".format(port))
        if port in self.write_ports:
            self.vf.write("  input [DATA_WIDTH-1:0]  DIN{0};\n".format(port))
        if port in self.read_ports:
            self.vf.write("  output [DATA_WIDTH-1:0] DOUT{0};\n".format(port))

    def add_write_block(self, port):
        """
        Add a write port block. Multiple simultaneous writes to the same address
        have arbitrary priority and are not allowed.
        """
        self.vf.write("\n")
        self.vf.write("  // Memory Write Block Port {0}\n".format(port))
        self.vf.write("  // Write Operation : When web{0} = 0, csb{0} = 0\n".format(port))
        self.vf.write("  always @ (negedge clk{0})\n".format(port))
        self.vf.write("  begin : MEM_WRITE{0}\n".format(port))
        if port in self.readwrite_ports:
            self.vf.write("    if ( !csb{0}_reg && !web{0}_reg )\n".format(port))
        else:
            self.vf.write("    if (!csb{0}_reg)\n".format(port))
        self.vf.write("        mem[ADDR{0}_reg] = DIN{0}_reg;\n".format(port))
        self.vf.write("  end\n")
        
    def add_read_block(self, port):
        """
        Add a read port block.
        """
        self.vf.write("\n")
        self.vf.write("  // Memory Read Block Port {0}\n".format(port))
        self.vf.write("  // Read Operation : When web{0} = 1, csb{0} = 0\n".format(port))
        self.vf.write("  always @ (negedge clk{0})\n".format(port))
        self.vf.write("  begin : MEM_READ{0}\n".format(port))
        if port in self.readwrite_ports:
            self.vf.write("    if (!csb{0}_reg && web{0}_reg)\n".format(port))
        else:
            self.vf.write("    if (!csb{0}_reg)\n".format(port))
        self.vf.write("       DOUT{0} <= #(DELAY) mem[ADDR{0}_reg];\n".format(port))
        self.vf.write("  end\n")
        
