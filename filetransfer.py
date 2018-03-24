
#Erick Terrazas G00776650
#I am testing if we can do software design without UDP SInk expected
#THis means we want to try file soruce and sinks which means saving to binary file 
#destinations. Keep in mind of file paths
#-------------------------------------------------------------------------------------------
#Lets start with our modules
from packetize import packetize
from subprocess import call		#for gnome terminal cmds
import glob						#for file searching
import sys,os
import fileManip 		#import split/comb def...Remember that this file must be in same diectory as sender.py!!
import time
import numpy as np
from shutil import rmtree as delete
#steps:
#1. get jpeg and split file into parts
#2. take each segment and add preamble,length, and name of segment
#3. combine the altered files back into one binary file
#4. FOr testing have allinonce.grc pick up file location and mod/demod
#5. Receive result file and see if binary file is the same
#NOTE: THIS IS NOT A MASTER PYTHON FILE DRAFT!!!!!!!!!!!!!!!!

#---------------------------step 1-------------------------------------------------------------
##Take  test jpeg file in directory and split it using fileManip definitions
intial = time.clock()

os.makedirs("INPUT") # Create the input folder to house the file partitions while code is running.

orig_file = 'sat_pic.JPG' #grab file name from cmd input
prefix = 'INPUT/pkt'			#Using string 'pic' for header later
preamble = 26530			#preamble for 'skipheader' gnuradio block
fsize = 1000			#Size of segments we want for split def (in bytes)

fileManip.cut(orig_file,prefix,fsize) #splits files and stores them to directory this python file is in


##Find segments, add its header ansd then 'stitch' into one big file again, with headers intact
final = ''			#final variable will hold compilationf of msg pylds that will have headrs in between segments
file_list = []		#This list will contain the filesnames of file segments
BER_CHECK = ''
print "----------------------------------------\nBEGIN FILE_LIST APPEND\n----------------------------------------"
for found in glob.glob(prefix+"*"):
	found = found.split('/')[1]	#create Nx2 list by seperating file name from prefix (OUTDATED)
	#print "found=:",found		#check whats the string in question
	file_list.append(found)		#add string into file_list[]
file_list.sort()

print "file_list:",file_list				#PRINT file_list(debug)


lenfieldsize =4 					#length added after filename will be four bytes exactly
new = packetize(preamble = preamble)					#create packetize class for data
for z in range(len(file_list)):
	tgt = open("INPUT/"+file_list[z],'rb')	#open each segment to variable 'tgt'
	pyld = tgt.read()					#actual pyld of pkt
##THIS SECTION IS FOR HEADER FIELD CREATION ATTACHMENT----------------------------------------------------------
	pyld_len = len(pyld)				#get length of pyld in BYTES
	fieldarray=list(str(pyld_len))		#turn data into '4 digit' str array ex 10 -->'' '' '1' '0'
	lenfield = np.pad(fieldarray,[lenfieldsize-len(fieldarray),0],"constant",constant_values=0)	#pad list with '' if no digit
	tmp = [0]*lenfieldsize
	for i in range(len(lenfield)):
		if lenfield[i] == '':
			lenfield[i] = '0'
		tmp[i] = int(lenfield[i])
	len_header = bytearray(tmp)		#we now have the length  field composed of four bytes 
##END LEN HEADER CREATION		---------------------------------------------------------------------------		   
	data = file_list[z] + len_header + pyld			#get orginal pyld with prefix and length header added on top
	tgt.close()							#close tgt file, now we have our seg. pyld
	segment = new.send(data)			#add header on top of data variable, store to segment variable
	final = final + segment				#'stitch' together segments to final pyld
	BER_CHECK += data					#Create a duplicate of expected output for BER testing without grc header
	#if (z==1):							#IADDED THIS SO ONLY 2PKTS WENT THROUGH (BER TESTING)
	#	break
	
###final needs 'trash pkts in case of gnu-radio syn, this means making a pkt9999 with a length of 100bytes of 'A', note it will need header stuff as well (trash-premable-length NO 2ndary header) [LISA protocol]
dummy_pkt_len = 100
dummy_pkt_data = ''
dummy_pyld = 'AAAAAAAAAAAA'
new = packetize(preamble = preamble)
dummy_pkt_data = 'pkt9999'					#first add dummy filename
dummy_pkt_data = dummy_pkt_data + dummy_pyld		#create one pyld of dummypkt with just pkt name
segment = new.send(dummy_pkt_data)			#add first level header to segment variable with dummy pkt to be sent thourgh gnuradio
final = segment + segment + segment + final + segment + segment + segment 		#ADDD 3 dummy pkts befoe and after relevant data
##final now has pyld mized in with dummy pkts, we will write this data into the binary file that will be inputted into TX_grc



GRC_input = open('TX_INPUT.bin','wb')	#create bin file that grc_tx will use as source OUTPUT of FILE
GRC_input.write(final)					#add all segments with headers into file
GRC_input.close()						#close file
#BER_sample = open('BER_samp.bin','wb')	#create binary file that will act as a check for BER in output bin file OUTPUT OF FILE
#BER_sample.write(BER_CHECK)
#BER_sample.close()
#delete("INPUT") # Delete the input folder after we're done.
final = time.clock()

print "Time Elapsed for Program:",final - intial				#TIMESTAMP for lines 1 -79


print "______________________________\nGRC_input is ready for allinone.grc\n\n______________________________"

##Now I'm just goign to open the binary file GRC_output and see what did the grc do to data

	
