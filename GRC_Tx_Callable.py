#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Grc Tx
# Generated: Sat Apr 14 15:58:24 2018
##################################################

from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import osmosdr
import time


class GRC_Tx(gr.top_block):

    def __init__(self,power):
        gr.top_block.__init__(self, "Grc Tx")

        ##################################################
        # Variables
        ##################################################
        self.baud_rate = baud_rate = 15e3
        self.BB_samp_rate = BB_samp_rate = 100e3
        self.sps = sps = int(BB_samp_rate/baud_rate)
        self.rf_freq = rf_freq = 0.915e9
        self.rf_bw = rf_bw = 5e6
        self.ifgain = ifgain = power
        self.const_points = const_points = 2
        self.channel_bw = channel_bw = 25e3
        self.RF_samp_rate = RF_samp_rate = 100000

        ##################################################
        # Blocks
        ##################################################
        self.osmosdr_sink_0 = osmosdr.sink( args="numchan=" + str(1) + " " + 'soapy=0,driver=lime,serial=0009061C02CF232D' )
        self.osmosdr_sink_0.set_sample_rate(RF_samp_rate)
        self.osmosdr_sink_0.set_center_freq(rf_freq, 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain(30, 0)
        self.osmosdr_sink_0.set_if_gain(ifgain, 0)
        self.osmosdr_sink_0.set_bb_gain(30, 0)
        self.osmosdr_sink_0.set_antenna('BAND1', 0)
        self.osmosdr_sink_0.set_bandwidth(5e6, 0)
          
        self.digital_psk_mod_0_0_0 = digital.psk.psk_mod(
          constellation_points=const_points,
          mod_code="gray",
          differential=True,
          samples_per_symbol=sps,
          excess_bw=0.35,
          verbose=False,
          log=False,
          )
        self.blocks_multiply_const_vxx_0_0_0 = blocks.multiply_const_vcc((.4, ))
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_char*1, '/home/odroid/Desktop/BER_TEST_OverCables/TX_INPUT.bin', True)
        (self.blocks_file_source_0).set_max_output_buffer(5000000)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_file_source_0, 0), (self.digital_psk_mod_0_0_0, 0))    
        self.connect((self.blocks_multiply_const_vxx_0_0_0, 0), (self.osmosdr_sink_0, 0))    
        self.connect((self.digital_psk_mod_0_0_0, 0), (self.blocks_multiply_const_vxx_0_0_0, 0))    

    def get_baud_rate(self):
        return self.baud_rate

    def set_baud_rate(self, baud_rate):
        self.baud_rate = baud_rate
        self.set_sps(int(self.BB_samp_rate/self.baud_rate))

    def get_BB_samp_rate(self):
        return self.BB_samp_rate

    def set_BB_samp_rate(self, BB_samp_rate):
        self.BB_samp_rate = BB_samp_rate
        self.set_sps(int(self.BB_samp_rate/self.baud_rate))

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps

    def get_rf_freq(self):
        return self.rf_freq

    def set_rf_freq(self, rf_freq):
        self.rf_freq = rf_freq
        self.osmosdr_sink_0.set_center_freq(self.rf_freq, 0)

    def get_rf_bw(self):
        return self.rf_bw

    def set_rf_bw(self, rf_bw):
        self.rf_bw = rf_bw

    def get_ifgain(self):
        return self.ifgain

    def set_ifgain(self, ifgain):
        self.ifgain = ifgain
        self.osmosdr_sink_0.set_if_gain(self.ifgain, 0)

    def get_const_points(self):
        return self.const_points

    def set_const_points(self, const_points):
        self.const_points = const_points

    def get_channel_bw(self):
        return self.channel_bw

    def set_channel_bw(self, channel_bw):
        self.channel_bw = channel_bw

    def get_RF_samp_rate(self):
        return self.RF_samp_rate

    def set_RF_samp_rate(self, RF_samp_rate):
        self.RF_samp_rate = RF_samp_rate
        self.osmosdr_sink_0.set_sample_rate(self.RF_samp_rate)


def main(top_block_cls=GRC_Tx, options=None):

    tb = top_block_cls()
    tb.start()
    tb.wait()


if __name__ == '__main__':
    main()
