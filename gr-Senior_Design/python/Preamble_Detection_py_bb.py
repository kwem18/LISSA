#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2018 <+YOU OR YOUR COMPANY+>.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import numpy
from gnuradio import gr


class Preamble_Detection_py_bb(gr.basic_block):
    """
    docstring for block tester_py_bb
    """
    # Create State Stuff
    SEARCH = 0
    HEADER = 1
    RUNNING = 2
    state = SEARCH

    def __init__(self, Preamble,Debug=False):
        #   WARNING:  PRINTING SLOWS DOWN EXECUTION SIGNIFICANTLY.   WARNING #
        #   WARNING:    MAY CAUSE ERRORS WHEN RUNNING REAL TIME.     WARNING #
        self.DebugPrints = Debug
        self.preamble = Preamble

        self.received_length = 0  # Keeps track of number of bytes received for current packet.
        self.packet_length = 0  # Number of bytes expected from packet
        self.preamblequeue = bytearray(1) # We will use a (32 bit) integer to check for the prefix.
        self.bitqueue = bytearray(1)
        self.bitcounter = 7
        self.headerqueue = [] # Create an empty list to hold bits of header.
        self.headersize = 4 # The header consists only of one integer for the size of the packet.
        gr.basic_block.__init__(self,
                            name="Preamble_Detection_py_bb",
                            in_sig=[numpy.byte],
                            out_sig=[numpy.byte])
        print("Getting startd. Preamble is set to: "+str(self.preamble))


    def forecast(self, noutput_items, ninput_items_required):
        # setup size of input_items[i] for work call
        # print "\nForecast called!"
        #if self.state != self.RUNNING:
        if True:
            for i in range(len(ninput_items_required)):
                ninput_items_required[i] = noutput_items
        #else:
        #    for i in range(len(ninput_items_required)):
        #        ninput_items_required[i] = 8*noutput_items
        # print "ninput_items_required: " + str(len(ninput_items_required))
        # print "noutput_items: " + str(noutput_items)


    def general_work(self, input_items, output_items):
        #print("General Work Called! State: "+str(self.state))
        #print("Length of input items 0: " + str(len(input_items[0])))
        #print("Lenth of output items 0: " + str(len(output_items[0])))

        #if len(input_items[0]) < 15:
         #   print("Input items 0: " + str(input_items[0]))
            #print("Lenth of output items 0: " + str(len(output_items[0])))
        #    raise NameError("\n\n\nToo many inputs for this test\n\n")
        # Hard value set by size of input/output items, determined by scheduler
        # Number of outputs is typically less than number of inputs.
        # This allows us to work on the maximum outputable number of inputs.

        # Search for the start of the packet. This will aline the bits.
        if self.state == self.SEARCH:
            #print("Searching for Preamble.")
            # Search for the preamble. Consume everything before preamble.
            # If preamble is found. Consume everything prior.
            # Only raise a flag, do not output anything yet.
            # Next call on real data will output correctly.
            count = 1
            for i in range(len(input_items[0])):
                self.preamblequeue[0] = (self.preamblequeue[0] << 1) & 0xFF
                self.preamblequeue[0] = self.preamblequeue[0] | (0x01 & input_items[0][i])
                if (self.preamblequeue[0] == self.preamble):
                    if self.DebugPrints:
                        print("Searching: Found preamble: " + str(self.preamblequeue[0]))
                    self.headerqueue = [] # Reset the headerqueue before we change state
                    self.preamblequeue = bytearray(1) # Reset the preamble queue for the next packet.
                    self.state = self.HEADER # Enter the header state
                    break
                count += 1
            self.consume(0, count)  # consumes 'count' of the inputs.
            #print("Searching: Consuming " + str(count) + " Inputs.\n\n")
            # Only consuming up to the prefix.
            # Data after prefix is handeled in next work call.
            # self.consume_each(count)
            data_to_output = 0  # There is no data to output before the prefix is found.

        # Parse through the header of the packet to determine it's properties.
        elif self.state == self.HEADER:
            # This should be the first state entered after the preamble was found.
            # print("\nBuffering the Header!")
            count = 0
            for i in range(len(input_items[0])):
                if len(self.headerqueue) == self.headersize:
                    break # If we have buffered all elements of the header, leave for loop.
                # print("\nbitcounter: " + str(bitcounter))
                count += 1
                self.bitqueue[0] = (self.bitqueue[0] & (0xFE << self.bitcounter)) & 0xFF  # Set the bit we are about to record to 0.
                # print("bitqueue[0] after 0 mask: " + str(self.bitqueue[0]))
                self.bitqueue[0] = (self.bitqueue[0] | (input_items[0][i] << self.bitcounter)) & 0xFF  # Set the bit coming into the input where it belongs
                # print("bitqueue[0] after bit recorded: " + str(self.bitqueue[0]))
                self.bitcounter += -1  # Decrement the bitcounter by 1.
                if self.bitcounter == -1:  # If the bit counter is -1, then we have packed a whole byte.
                    #print("Header: Packed Bitqueue: " + str(self.bitqueue[0]))
                    self.bitcounter = 7 # Reset the bitcounter for the next byte.
                    self.headerqueue.append(self.bitqueue[0])
            if len(self.headerqueue) == self.headersize: # We have the whole header, time to parse!
                # print("Parsing Header!")
                # Reset header values.
                self.packet_length = 0
                for i in range(len(self.headerqueue)):
                    if i < 4: # This is the first section of the header, the packet length
                        self.packet_length += self.headerqueue[i] * numpy.power(10, (3 - i))
                if self.packet_length > 10000:
                    if self.DebugPrints:
                        print("Header: Packet length "+str(self.packet_length)+" is too large. Assuming noise, restarting search.")
                    self.state = self.SEARCH
                else:
                    if self.DebugPrints:
                        print("Header: Packet length determined as "+str(self.packet_length))
                    self.state = self.RUNNING
                    #print("Header: Switching to running state.")
                # print("Packet Length determined as: "+str(self.packet_length))

            self.consume(0, count)  # Consume how ever many inputs were used in the for loop.
            #print("Header: Consuming " + str(count) + " Inputs.\n\n")
            data_to_output = 0  # There is no data to output when parsing header.

        # Pass packet data to the output of the block.
        elif self.state == self.RUNNING:
            # print("\nOutputting data after the preamble was found.")
            count = 0
            data_to_output = 0
            for i in range(len(input_items[0])):
                count += 1 # We've consumed another bit of data.
                #print("Running: Incrementing Count ("+str(count)+")")
                #print("Running: bitcounter: " + str(self.bitcounter))
                self.bitqueue[0] = (self.bitqueue[0] & (0xFE << self.bitcounter)) & 0xFF  # Set the bit we are about to record to 0.
                #print("Running: bitqueue after 0 mask: " + str(self.bitqueue[0]))
                self.bitqueue[0] = (self.bitqueue[0] | (
                            input_items[0][i] << self.bitcounter)) & 0xFF  # Set the bit coming into the input where it belongs
                #print("Running: Bit being recorded: "+ str(input_items[0][i]))
                #print("bitqueue after bit recorded: " + str(self.bitqueue[0]))
                self.bitcounter += -1  # Decrement the bitcounter by 1.
                if self.bitcounter == -1:  # If the bit counter is -1, then we have packed a whole bit.
                    if self.DebugPrints:
                        print("Running: Packed Bitqueue: " + str(self.bitqueue[0]))
                    self.bitcounter = 7
                    self.received_length += 1
                    output_items[0][data_to_output] = self.bitqueue[0]
                    data_to_output += 1
                    # Remember, Data to output is a counter used by gnuradio to determine num of data outputs for block
                    # It is not only a counter.
                    if self.received_length == self.packet_length:  # We've received the whole packet.
                        # Lower the flags.
                        if self.DebugPrints:
                            print("Running: Entire packet was received! Resetting state.")
                        self.state = self.SEARCH  # Start looking for the start of the next packet.
                        self.received_length = 0
                        break
            #print("Running: Current bitcounter state: " + str(self.bitcounter))
            #print("Running: Current bitqueue state:   " + str(int(self.bitqueue[0])))
            if self.DebugPrints:
                print("Running: Consuming " + str(count) + " Inputs.\n\n")
            #if count == 10:
            #    print("Input Data: "+str(input_items[0]))
            self.consume(0, count)  # Consumes all used inputs
        else:
            print("No State: Something happened.")
            self.state = self.SEARCH
            data_to_output = 0

        # self.consume_each(consumable)
        return data_to_output
