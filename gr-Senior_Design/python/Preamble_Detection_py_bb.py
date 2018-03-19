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

    def __init__(self, Preamble, Debug=0):
        #   WARNING:  PRINTING SLOWS DOWN EXECUTION SIGNIFICANTLY.   WARNING #
        #   WARNING:    MAY CAUSE ERRORS WHEN RUNNING REAL TIME.     WARNING #
        self.DebugPrints = Debug
        self.preamble = Preamble

        self.received_length = 0  # Keeps track of number of bytes received for current packet.
        self.packet_length = 0  # Number of bytes expected from packet
        self.preamblequeue = 0  # We will use a (32 bit) integer to check for the prefix.
        self.bitqueue = bytearray(1)
        self.bitcounter = 7
        self.headerqueue = []  # Create an empty list to hold bits of header.
        self.headersize = 4  # The header consists only of one integer for the size of the packet.
        gr.basic_block.__init__(self,
                                name="Preamble_Detection_py_bb",
                                in_sig=[numpy.byte],
                                out_sig=[numpy.byte])
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
        print("Getting started. Preamble is set to: " + str(self.preamble))
        print("Version 3.19.18...")

    def forecast(self, noutput_items, ninput_items_required):
        # setup size of input_items[i] for work call
        # print "\nForecast called!"
        # if self.state != self.RUNNING:
        if True:
            for i in range(len(ninput_items_required)):
                ninput_items_required[i] = noutput_items
        # else:
        #    for i in range(len(ninput_items_required)):
        #        ninput_items_required[i] = 8*noutput_items
        # print "ninput_items_required: " + str(len(ninput_items_required))
        # print "noutput_items: " + str(noutput_items)

    def general_work(self, input_items, output_items):
        count = -1  # Count set to -1 because each for loop initiates at current count +1
        data_to_output = 0
        if self.DebugPrints >= 2:
            print("General: Startup: Input Items Length = " + str(len(input_items[0])))
        while count < len(input_items[0])-1:
            # Search for the start of the packet. This will aline the bits.
            if self.state == self.SEARCH:
                # If preamble is found. Consume everything prior.
                # Only raise a flag, do not output anything yet.
                if self.DebugPrints >= 1:
                    print("General: Searching: Starting.")
                for count in range(count + 1, len(input_items[0])):
                    if self.DebugPrints >= 4:
                        print("General: Searching: Inside For Loop. Count = " + str(count))
                    if self.DebugPrints >= 4:
                        print("General: Searching: Count = " + str(count) + ", Value = " + str(input_items[0][count]))
                    self.preamblequeue = (
                                                     self.preamblequeue << 1) & 0xFFFFFFFF  # shift then mask to ensure that we stay at 32 bits
                    self.preamblequeue = self.preamblequeue | (
                                0x01 & input_items[0][count])  # Set the LSB of input to LSB of queue
                    if self.DebugPrints >= 3:
                        print("General: Searching: PreambleQueue: " + str(self.preamblequeue))
                    if self.preamblequeue == self.preamble:
                        if self.DebugPrints >= 0:
                            print("General: Searching: Found preamble: " + str(self.preamblequeue))
                        self.headerqueue = []  # Reset the headerqueue before we change state
                        self.preamblequeue = 0  # Reset the preamble queue for the next packet.
                        self.state = self.HEADER  # Enter the header state
                        break

            # Parse through the header of the packet to determine it's properties.
            elif self.state == self.HEADER:
                # This should be the first state entered after the preamble was found.
                if self.DebugPrints >= 1:
                    print("General: Header: Starting.")
                for count in range(count + 1, len(input_items[0])):
                    self.bitqueue[0] = (self.bitqueue[0] & (
                                0xFE << self.bitcounter)) & 0xFF  # Set the bit we are about to record to 0.
                    self.bitqueue[0] = (self.bitqueue[0] | (input_items[0][
                                                                count] << self.bitcounter)) & 0xFF  # Set the bit coming into the input where it belongs
                    self.bitcounter += -1  # Decrement the bitcounter by 1.
                    if self.bitcounter == -1:  # If the bit counter is -1, then we have packed a whole byte.
                        self.bitcounter = 7  # Reset the bitcounter for the next byte.
                        self.headerqueue.append(self.bitqueue[0])
                    if len(self.headerqueue) == self.headersize:
                        if self.DebugPrints >= 1:
                            print("General: Header: Parsing Header!")
                        # Reset header values.
                        self.packet_length = 0
                        for i in range(len(self.headerqueue)):
                            if self.DebugPrints >= 5:
                                print("General: Header: Inside For Loop. Count = " + str(count))
                            if i < 4:  # This is the first section of the header, the packet length
                                self.packet_length += self.headerqueue[i] * numpy.power(10, (3 - i))
                        if self.packet_length > 10000:
                            if self.DebugPrints >=1:
                                print("General: Header: Packet length " + str(
                                    self.packet_length) + " is too large. Assuming noise, restarting search.")
                            self.state = self.SEARCH
                        else:
                            if self.DebugPrints >=0:
                                print("General: Header: Packet length determined as " + str(self.packet_length))
                            self.state = self.RUNNING
                        break  # If we have buffered all elements of the header, leave for loop.

            # Pass packet data to the output of the block.
            elif self.state == self.RUNNING:
                if self.DebugPrints >= 2:
                    print("General: Running: Started.")
                for count in range(count + 1, len(input_items[0])):
                    if self.DebugPrints >= 5:
                        print("General: Running: Inside For Loop. Count = " + str(count))
                    self.bitqueue[0] = (self.bitqueue[0] & (
                                0xFE << self.bitcounter)) & 0xFF  # Set the bit we are about to record to 0.
                    self.bitqueue[0] = (self.bitqueue[0] | (
                            input_items[0][
                                count] << self.bitcounter)) & 0xFF  # Set the bit coming into the input where it belongs
                    self.bitcounter += -1  # Decrement the bitcounter by 1.
                    if self.bitcounter == -1:  # If the bit counter is -1, then we have packed a whole bit.
                        if self.DebugPrints>=0:
                            print("Running: Packed Bitqueue: " + str(self.bitqueue[0]))
                        self.bitcounter = 7
                        self.received_length += 1
                        output_items[0][data_to_output] = self.bitqueue[0]
                        data_to_output += 1
                        # Remember, Data to output is a counter used by gnuradio to determine num of data outputs for block
                        # It is not only a counter.
                        if self.received_length == self.packet_length:  # We've received the whole packet.
                            # Lower the flags.
                            if self.DebugPrints>=2:
                                print("General: Running: Entire packet was received! Resetting state.")
                            self.state = self.SEARCH  # Start looking for the start of the next packet.
                            self.received_length = 0
                            break
            else:
                print("General: No State: Something happened.")
                self.state = self.SEARCH
            if self.DebugPrints >= 3:
                print("General: Finished Loop.")

        # self.consume_each(consumable)
        if self.DebugPrints >= 1:
            print("General: Leaving: Consuming = " + str(count + 1))
            print("General: Leaving: Outputting = " + str(data_to_output))
            if data_to_output != 0:
                print("General: Leaving: DATA OUTPUTTED!")
                print(output_items[0][0:data_to_output])
        self.consume(0, count+1) # Count is used as an index and starts at 0, must consume 0th input though.
                                 # Consume is done using counting numbers, so index 0-4 would be 5 things consumed
        return data_to_output
