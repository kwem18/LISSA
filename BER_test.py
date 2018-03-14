#BER TEST Erick Terrazas G00776650
#Last edit made on 3/13/18
from pathlib import Path
import os
import sys
import time
import glob
#sys.argv[1]
#--------------------------------------------------------------------------
def BERTEST(filename_in):
	file = str(filename_in)				#INPUT FILENME MUST BE PUT IN HERE
	filecheck = "OUTPUT/"+ file
	fpath0 = Path(file)
	fpath = Path(filecheck)
	print "Checking packet:",file
	if (fpath0.is_file() & fpath.is_file()):
		print "PACKET exists"
		
	else:
		print "PACKET DROPPED"
		return
		
	f = open(file,'rb')					#open test file
	h = open(filecheck,'rb')		#ACCESS FILE in OUTPUT FOLDER
	print "Packet Target:",file
	switch = 1
	counter = 7
	input_list = []
	output_list = []
	bit_error_count = 0
	while(switch==1):
		counter = 7
		byte = f.read(1)
		byte1 = h.read(1)
		if byte:
			byte_list = []
			byte_list1 = []
			while (counter>=0):
				number = ord(byte)
				number1 = ord(byte1)
				bit = (number>>counter) & (0x01)  #create bit for list index
				bit1 = (number1>>counter) & (0x01)
				byte_list.append(bit)             #add bit to list
				byte_list1.append(bit1)
				counter -= 1
        
			input_list.append(byte_list)
			output_list.append(byte_list1)
		else:
			switch = 0
	f.close()
	h.close()
	bit_error_count = 0 #counter for number of bit inconsistencies
	for x in range(len(input_list)):
		for y in range(len(input_list[0])):
			if input_list[x][y] == output_list[x][y]:
				continue
			else:
				bit_error_count += 1
				print "Bit error at byte",x
				print "at bit number", y
				print "INPUT BYTE:",input_list[x]
				print "OUTPUT BYTE:",output_list[x]
				print "\n------------------------------------------------"
	print "Total number of bits lost:",bit_error_count
	print "END PACKET:",file
	return 			
	
	
#MAIN FUNCTION--------------------------------------------------------------------------------------------------------------------------

###PACKETS DROPPED CHECK START
print "Testing output packets\n-----------------\n-----------------\n-----------------"
outputf = open("GRC_output.bin",'rb')		#open grc output_list
lever = 1 
									#For while loop
while(lever==1):
	length = 0
	name = outputf.read(7)					#read pkt name save it
	if name:
		byte = outputf.read(1)				#read length based on int value of each byte
		if not byte:
			print "length of payload < field length value, escaping definition."
			lever = 0
		length += ord(byte)*1000
		byte = outputf.read(1)
		if not byte:
			print "length of payload < field length value, escaping definition."
			lever = 0
		length += ord(byte)*100
		byte = outputf.read(1)
		if not byte:
			print "length of payload < field length value, escaping definition."
			lever = 0
		length += ord(byte)*10
		byte = outputf.read(1)
		if not byte:
			print "length of payload < field length value, escaping definition."
			lever = 0
		length += ord(byte)					#length calculated
		
		msg = outputf.read(length)			#get pyld
		r = open("OUTPUT/"+name,'wb')		#make new file at OUTPUT folder using name
		r.write(msg)						#put pyld into new file	
		r.close() 					#close file
	else:		
		outputf.close()
		lever = 0

###NOW we have an input segment in main dir., and its corresponding input in OUTPUT folder
#-We have to make a list of both file groups to calculate files dropped\n------------------------------------
otpt_list = []
inpt_list = []
print "Calculating packets dropped...\n-----------------\n-----------------\n-----------------"
for found in glob.glob("OUTPUT/pkt*"):	#Create list for output packets
	found = found.split('/')[1]			#Isolate pktXXXX
	otpt_list.append(found)				#add name to array
	
for piece in glob.glob("pkt*"):			#create list for input packets
	inpt_list.append(piece)

droppedpkt = len(inpt_pkt) - len(otpt_pkt) #use length of list to determine # of pkts dropped
print"\nTOTAL NUMBER OF PACKETS DROPPED:",droppedpkt
	
###Now we have a list of packets, lets compare!
droppedpkt = 0
for target in range(len(inpt_list)):
	BERTEST(target)  #BERTEST def should either return 1 or 0
	

print"END TEST\n-----------------------------------------------------"
	
	


	
