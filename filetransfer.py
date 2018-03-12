# Erick Terrazas G00776650
# I am testing if we can do software design without UDP SInk expected
# THis means we want to try file soruce and sinks which means saving to binary file
# destinations. Keep in mind of file paths
# -------------------------------------------------------------------------------------------
# Lets start with our modules
from packetize import packetize
from subprocess import call  # for gnome terminal cmds
import glob  # for file searching
import sys, os
import fileManip  # import split/comb def...Remember that this file must be in same diectory as sender.py!!
import time
import numpy as np

# steps:
# 1. get jpeg and split file into parts
# 2. take each segment and add preamble,length, and name of segment
# 3. combine the altered files back into one binary file
# 4. FOr testing have allinonce.grc pick up file location and mod/demod
# 5. Receive result file and see if binary file is the same
# NOTE: THIS IS NOT A MASTER PYTHON FILE DRAFT!!!!!!!!!!!!!!!!

# ---------------------------step 1-------------------------------------------------------------
## Take  test jpeg file in directory and split it using fileManip definitions
print "Time:", time.clock()

orig_file = 'small_pkt.txt'  # grab file name from cmd input
prefix = 'pkt'  # Using string 'pic' for header later
preamble = 26530  # preamble for 'skipheader' gnuradio block
fsize = 10  # Size of segments we want for split def (in bytes)

fileManip.cut(orig_file, prefix, fsize)  # splits files and stores them to directory this python file is in

## Find segments, add its header ansd then 'stitch' into one big file again, with headers intact
final = ''  # final variable will hold compilationf of msg pylds that will have headrs in between segments
file_list = []  # This list will contain the filesnames of file segments
BER_CHECK = ''
print "----------------------------------------\nBEGIN FILE_LIST APPEND\n----------------------------------------"
for found in glob.glob("pkt*"):
    # found = found.split('/')[1]	#create Nx2 list by seperating file name from prefix (OUTDATED)
    # print "found=:",found		#check whats the string in question
    file_list.append(found)  # add string into file_list[]

print "file_list:", file_list  # PRINT file_list(debug)

lenfieldsize = 4  # length added after filename will be four bytes exactly
for z in range(len(file_list)):
    tgt = open(file_list[z], 'rb')  # open each segment to variable 'tgt'
    pyld = tgt.read()  # actual pyld of pkt
    ## THIS SECTION IS FOR HEADER FIELD CREATION ATTACHMENT----------------------------------------------------------
    pyld_len = len(pyld)  # get length of pyld in BYTES
    fieldarray = list(str(pyld_len))  # turn data into '4 digit' str array ex 10 -->'' '' '1' '0'
    lenfield = np.pad(fieldarray, [lenfieldsize - len(fieldarray), 0], "constant", constant_values=0)
    tmp = [0] * lenfieldsize
    for i in range(len(lenfield)):
        if lenfield[i] == '':
            lenfield[i] = '0'
        tmp[i] = int(lenfield[i])
    len_header = bytearray(tmp)  # we now have the length  field composed of four bytes
    ## END LEN HEADER CREATION		---------------------------------------------------------------------------
    data = file_list[z] + len_header + pyld  # get orginal pyld with prefix and length header added on top
    tgt.close()  # close tgt file, now we have our seg. pyld
    new = packetize(preamble = preamble)  # create packetize class for data
    segment = new.send(data)  # add header on top of data variable, store to segment variable
    final = final + segment  # 'stitch' together segments to final pyld
    BER_CHECK += data  # Create a duplicate of expected output for BER testing without grc header
    if (z == 1):  # IADDED THIS SO ONLY 2PKTS WENT THROUGH (BER TESTING)
        break

GRC_input = open('TX_INPUT.bin', 'wb')  # create bin file that grc_tx will use as source
GRC_input.write(final)  # add all segments with headers into file
GRC_input.close()  # close file
BER_sample = open('BER_samp.bin', 'wb')  # create binary file that will act as a check for BER in output bin file
BER_sample.write(BER_CHECK)
BER_sample.close()

print "Time:", time.clock()  # TIMESTAMP for lines 1 -79

print "______________________________\nGRC_input is ready for allinone.grc\n\n______________________________"

##Now I'm just goign to open the binary file GRC_output and see what did the grc do to data
