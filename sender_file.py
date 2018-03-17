#Erick Terrazas G00776650 
#SENDER_FILE.PY
#I am creating this quick outline if file sink/source becomes a viable route
#Notes:
#	-The input binary file MUST be ready before grc is activated
#	-Output of tx_grc will be to antenna, and output of grc_rx is a file sink
#	-We need to import ADAFRUIT stuff here as well

#FILES NEEDED IN DIRECTORY:
#WIll's jpeg creation file
#packetize.py
#GRC files for Tx and Rx
# binary files for data transfer

###MODULES
import numpy as np
from packetize import packetize
import time						#timestamp uses
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.FT232H as FT232H
from subprocess import call		#for gnome terminal cmds
import glob						#for file searching
import sys
import fileManip 		#import split/comb def...Remember that this file must be in same diectory as sender.py!!

#-----------------------------------------------------------------------------------------
###Initialize out GPIO board

FT232H.use_FT232H()  		#temporarily disable FTDI serial driver
ft232h = FT232H.FT232H()  	#finds device

ft232h.setup(8,GPIO.OUT)		#pin 1 maps to pin D0 on GPIO board
#ft232h.setup(1,GPIO.OUT)		#MAYBE FOR LED LIGHTS???

#-----------------------------------------------------------------------------------------
### HERE is the code run in order for the following:

#	-picture taken by camera
#	-picture turned into jpeg
#	-picture saved to directory
#	-Sperate py file for data recovery? ('file_rec.py')
#-----------------------------------------------------------------------------------------

### Take jpeg and prepare for grc_tx

init= time.clock()			#TIMESTAMP
orig_file = 'test1.JPG' #grab file name from cmd input (argv[1])
prefix = 'pic'			#Using string 'pic' for header later
preamble = 5			#preamble for 'skipheader' gnuradio block
fsize = 1000			#Size of segments we want for split def

fileManip.cut(orig_file,prefix,fsize) #splits files and stores them to directory this python file is in


##Find segments, add its header ansd then 'stitch' into one big file again, with headers intact
final = ''			#Holds cumulative pyld data taken from segments
file_list = []		#This list will contain the filesnames of file segments

print "----------------------------------------\nSTART FILE_LIST APPEND\n----------------------------------------"
for found in glob.glob("pic*"):
	#found = found.split('/')[1]	#create Nx2 list by seperating file name from prefix (OUTDATED)
	#print "found=:",found		#check whats the string in question
	file_list.append(found)		#add string into file_list[]
	file_list.sort()

print "file_list:",file_list				#PRINT file_list(debug)
BER_test = ''
lenfieldsize = 4					#desired size of length header in bytes

for z in range(len(file_list)):			#use list to open and add to data segments
	tgt = open(file_list[z],'rb')		#open each segment to variable 'tgt'
	pyld = tgt.read()					#get payload data for length header
	###THIS SECTION IS FOR HEADER FIELD CREATION ATTACHMENT----------------------------------------------------------
	pyld_len = len(pyld)				#get length of pyld in BYTES
	fieldarray=list(str(pyld_len))		#turn data into '4 digit' str array ex 10 -->'' '' '1' '0'
	lenfield = np.pad(fieldarray,[lenfieldsize-len(fieldarray),0],"constant",constant_values=0)
	tmp = [0]*lenfieldsize
	
	for i in range(len(lenfield)):		#2nd for loop prepeares len_header to have desired length field
		if lenfield[i] == '':			#turns an empty byte to '0' in list
			lenfield[i] = '0'
		tmp[i] = int(lenfield[i])
	len_header = bytearray(tmp)		#we now have the length  field composed of four bytes 
	##END LEN HEADER CREATION		---------------------------------------------------------------------------	

	data = file_list[z] + len_header + pyld	#get orginal pyld with prefix and 2ndary length header added on top
	tgt.close()								#close tgt file, now we have our seg. pyld
	new = packetize()						#create packetize class for data
	segment = new.send(data)				#add header on top of data variable, store to segment variable
	final = final + segment					#'stitch' together segments to final pyld
	BER_test += data						#BER_test will provide smaple output for later(precaution)
#END FOR LOOP	
GRC_input = open('TX_INPUT.bin','wb')	#create bin file that grc_tx will use as source
GRC_input.write(final)					#add all segments with headers into input binary file
GRC_input.close()						#close file
BER = open('BER_samp.py','wb')			#Create smaple file that shows expected output after Rx 
BER.write(BER_test)
BER.close()
print "-----------Time Displacement(seconds):",(time.clock()-init),"-----------"		#Timestamp
#----------------------------------------------------------------------------------------------------

###binary file now will have its data sent out of antenna via GNURADIO
#------>BEGIN TX MODE

#FLIP GPIO TO TX!!!
ft232h.output(8,GPIO.HIGH)			#TURN ON TX HARDWARE

#cmd for gnuradio_tx file
#call(['gnome-terminal','--','./grc_tx.py']) #Opens grc for TX (TURN OFF ACTION TBD)
time.sleep(1)
#Data now sent over antenna, Tx is complete

#-----> END TX MODE
#-----------------------------------------------------------------------------------------
###Prepare device for reception of data from satellite
#----->BEGIN RX MODE

#FLIP GPIO TO RX!!!
#ft232h.output(8,GPIO.LOW)			#TURN ON RX HARDWARE

#call grc_rx file
#call(['gnome-terminal','--','./grc_rx.py']) #Opens grc for TX (TURN OFF TBD)

#And then we wait........

#[fileserver.py for bin file????]


#----->End RX MODE
#-----------------------------------------------------------------------------------------

### Once msg received, rUn BER_TEST.py and check packet drop and BER using grc rx file sink (grc_output.bin)

#END FILE-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_