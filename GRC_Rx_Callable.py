#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Grc Rx
# Generated: Sat Apr 14 15:58:18 2018
##################################################

from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import Senior_Design
import correctiq
import osmosdr
import time


class GRC_Rx(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Grc Rx")

        ##################################################
        # Variables
        ##################################################
        self.baud_rate = baud_rate = 15e3
        self.BB_samp_rate = BB_samp_rate = 100e3
        self.sps = sps = int(BB_samp_rate/baud_rate)
        self.rf_freq = rf_freq = 0.915e9
        self.rf_bw = rf_bw = 5e6
        self.const_points = const_points = 2
        self.channel_bw = channel_bw = 25e3
        self.RF_samp_rate = RF_samp_rate = 100000

        ##################################################
        # Blocks
        ##################################################
        self.osmosdr_source_0 = osmosdr.source( args="numchan=" + str(1) + " " + 'soapy=0,driver=lime,serial=0009070105C62E09' )
        self.osmosdr_source_0.set_sample_rate(RF_samp_rate)
        self.osmosdr_source_0.set_center_freq(rf_freq, 0)
        self.osmosdr_source_0.set_freq_corr(0, 0)
        self.osmosdr_source_0.set_dc_offset_mode(0, 0)
        self.osmosdr_source_0.set_iq_balance_mode(0, 0)
        self.osmosdr_source_0.set_gain_mode(False, 0)
        self.osmosdr_source_0.set_gain(0, 0)
        self.osmosdr_source_0.set_if_gain(10, 0)
        self.osmosdr_source_0.set_bb_gain(10, 0)
        self.osmosdr_source_0.set_antenna('LNAW', 0)
        self.osmosdr_source_0.set_bandwidth(rf_bw, 0)
          
        self.digital_psk_demod_0_0_0 = digital.psk.psk_demod(
          constellation_points=const_points,
          differential=True,
          samples_per_symbol=sps,
          excess_bw=0.35,
          phase_bw=6.28/100.0,
          timing_bw=6.28/100.0,
          mod_code="gray",
          verbose=False,
          log=False,
          )
        self.digital_costas_loop_cc_0 = digital.costas_loop_cc(0.99, const_points, False)
        self.correctiq_correctiq_0 = correctiq.correctiq()
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_char*1, '/home/odroid/Desktop/BER_TEST_OverCables/Output', False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.Senior_Design_Preamble_Detection_py_bb_0 = Senior_Design.Preamble_Detection_py_bb(26530, 1)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.Senior_Design_Preamble_Detection_py_bb_0, 0), (self.blocks_file_sink_0, 0))    
        self.connect((self.correctiq_correctiq_0, 0), (self.digital_costas_loop_cc_0, 0))    
        self.connect((self.digital_costas_loop_cc_0, 0), (self.digital_psk_demod_0_0_0, 0))    
        self.connect((self.digital_psk_demod_0_0_0, 0), (self.Senior_Design_Preamble_Detection_py_bb_0, 0))    
        self.connect((self.osmosdr_source_0, 0), (self.correctiq_correctiq_0, 0))    

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
        self.osmosdr_source_0.set_center_freq(self.rf_freq, 0)

    def get_rf_bw(self):
        return self.rf_bw

    def set_rf_bw(self, rf_bw):
        self.rf_bw = rf_bw
        self.osmosdr_source_0.set_bandwidth(self.rf_bw, 0)

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
        self.osmosdr_source_0.set_sample_rate(self.RF_samp_rate)


def main(top_block_cls=GRC_Rx, options=None):

    tb = top_block_cls()
    tb.start()
    tb.wait()


if __name__ == '__main__':
    main()
