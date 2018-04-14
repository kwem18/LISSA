#BER TEST Erick Terrazas G00776650
#Last edit made on 3/24/18

#NOTES: THis program needs BER_samp.bin, and the received bin file from GRC_RX 
from subprocess import call		#For gnome terminal call cmd
from pathlib import Path
from matplotlib.pyplot import *		#FOr data gathering
import os
import sys
import time
import glob
import cPickle			#same as pickle module but allegedyly "1000 times faster"

avg_bit_loss = []		#glbl var list avg bits lost for only rcvd pkts
total_bit_loss = []     #percentage of bits lost for every pkt including dropped pkts

#------------------------------------------------------------------------------------------------------------------------------------
def BERTEST(filename_in,debug=0):
	global avg_bit_loss
	global total_bit_loss
	file = str(filename_in)				#INPUT FILENAME MUST BE PUT IN HERE
	filecheck0= "INPUT/" + file			#Path of input pkt at INPUT folder of directory
	filecheck1 = "Outputs/"+ file		#Path of POSSIBLE received packet at OUTPUT folder of directory
	if debug >= 0:
		print "BERTEST for packet:",file	#State the name of pkt we are hecking for inconsistencies with test pkt
	fpath0 = Path(filecheck0)					#designates the path of input filename with respect to main directory
	fpath = Path(filecheck1)				#designates the path of output filename with respect to main directory
	
	if (fpath0.is_file() & fpath.is_file()):
		if debug >= 1:
			print "/////////////////////////////////////////////////////////////////////////////\nPACKET exists for:",file
			print "\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n"
			  
		
	else:
		total_bit_loss.append(float(1))  #acknowledge 100% which implies lost pkt for plot graph of %bitloss vs pktnumber
		if debug >= 1:
			print "\n##############################\nPACKET DROPPED for:",file
			print "##############################\n"
			print "-----------------------------------------------------------------------------#\n"
		return
		
	f = open(filecheck0,'rb')					#ACESS TEST FILE in INPUT FOLDER
	h = open(filecheck1,'rb')					#ACCESS FILE in OUTPUT FOLDER
	switch = 1
	counter = 7
	input_list = []					#list in order to indicate byte and bit location of data
	output_list = []				#list output for byte and bit location of data
	bit_error_count = 0				#define bit error count for packet
	while(switch==1):				#while loop used in order to read a byte for input & output and place them into their respective lists
		counter = 7
		beta = f.read(1)			#beta holds byte read from input pkt  	<---------------------------
		beta1 = h.read(1)			#beta1 holds byte read from output pkt	<---------------------------
		
		if beta:
			if beta1:
				byte_list = []			#this smaller list will hold a byte of input pkt payload
				byte_list1 = []			#holds byte of output pkt payload
				while (counter>=0):
					number = ord(beta)				#number will have number representation of byte using ord() function
					number1 = ord(beta1)
					bit = (number>>counter) & (0x01)  #create bit for list index
					bit1 = (number1>>counter) & (0x01)
					byte_list.append(bit)             #add bit to input byte list
					byte_list1.append(bit1)			  #add bit to output byte list
					counter -= 1
			
			else:
				if debug >= 0:
					print "||||||||||||||||||||||||||||||\nOUTPACKET LENGTH IS LESS THAN INPUT! DROPPING PACKET\n||||||||||||||||||||||||||||||",file
				return
        
			input_list.append(byte_list)		#append byte_list into input_list ex (byte_list = [ [0,0,0,1,0,1,0,0] , [0,0,0,0,0,0,0,0] , ... ])
			output_list.append(byte_list1)
		else:
			switch = 0
			break
	f.close()								#CLOSE INPUT TEST FILE
	h.close()								#CLOSE OUTPUT FILE
	bit_error_count = 0							 #counter for number of bit inconsistencies
	for x in range(len(input_list)):					#for loop uses x at byte value, and y as bit number
		flag = 0
		for y in range(len(input_list[0])):
			if input_list[x][y] == output_list[x][y]:		#Nothing happens if bit locations from both lists are the same
				continue
			else:											#difference in bit value leads to acknowledgment of a bi error
				bit_error_count += 1
				flag = 1
		if flag == 1:
			dif = "["
			for i in range(8):
				if input_list[x][i] == output_list[x][i]:
					dif = dif + " , "
				else:
					dif = dif + "x, "
			dif = dif[0:23] + "]"

			if debug >= 1:
				print "Bit error in packet ",file,"at byte",x
				print "INPUT  BYTE:",input_list[x]			#show byte where error occurred
				print "OUTPUT BYTE:",output_list[x]
				print "            ",dif
			#print "\n------------------------------------------------"
	pkt_bit_loss = float(bit_error_count)/float(len(input_list)*8)
	avg_bit_loss.append(pkt_bit_loss) 			#Add percentage loss to grand list, will divide by existing pkts later in main function
	total_bit_loss.append(pkt_bit_loss) 		#Add percentage to grand total for plot
	if debug >= 0:
		print "Percentage of bits lost:",pkt_bit_loss		#Print BER for pkt being checked at the the time of defintion being used
		print "\nEND BERTEST OF:",file
		print "\n-----------------------------------------------------------------------------#\n"
	return 	#Leave definition		
	
	
#MAIN FUNCTION--------------------------------------------------------------------------------------------------------------------------
#########################################################################################################################################

###PACKETS DROPPED CHECK START
###WE first strip secondary header of of GR_rx output binary file
#We create an output pkt and store it into the OUTPUT folder, this process ends at line 139
#print "Stripping output packets out of file and into OUTPUT folder\n-----------------\n-----------------\n-----------------"
#outputf = open("Output",'rb')		#open grc output_list.  
#lever = 1 
									#For while loop
#while(lever==1):
#	length = 0
#	name = outputf.read(7)					#read pkt name save it to variable 'name'
#	if name:
#		alpha = outputf.read(1)			#read length based on int value of each byte
#		if (not alpha) or len(alpha)==0:
#			print "\nlength of payload < field length value, escaping definition.\n"
#			lever = 0
#			break
#		length += (ord(alpha)*1000)
#		alpha = outputf.read(1)
#		if (not alpha) or len(alpha)==0:
#			print "\nlength of payload < field length value, escaping definition.\n"
#			lever = 0
#			break
#		length += (ord(alpha)*100)
#		alpha = outputf.read(1)
#		if (not alpha) or len(alpha)==0:
#			print "\nlength of payload < field length value, escaping definition.\n"
#			lever = 0
#			break
#		length += (ord(alpha)*10)
#		alpha = outputf.read(1)
#		if (not alpha) or len(alpha)==0:
#			print "\nlength of payload < field length value, escaping definition.\n"
#			lever = 0
#			break
#		length += ord(alpha)					#length calculated
#		
#		msg = outputf.read(length)			#get payload
#		r = open("OUTPUT/"+name,'wb')		#make new file at OUTPUT folder using name
#		r.write(msg)						#put payload into new file	
#		r.close() 							#close file
#	else:
#		print "DIDN'T READ DATA! ESCAPING DEFINITION"
#		outputf.close()
#		lever = 0
#		break
#print "OUT pkts now in OUTPUT folder\n----------\n----------\n----------"


#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
###NOW we have an input segment in main dir., and its corresponding output pkt in OUTPUT folder NOTE: NOW DONE IN OUTINTERPRET.py

def test(testName,snr,folder,debug=0):
	#-We have to make a list of both file groups to calculate files dropped\n------------------------------------
	# Reset global variables every time it's run
	global avg_bit_loss  # glbl var list avg bits lost for only rcvd pkts
	global total_bit_loss
	avg_bit_loss = []
	total_bit_loss = []
	otpt_list = []		#This list will have the filenames of packets we outputted from Rx grc
	inpt_list = []		#This list will have the filenames of packets we inputted into Tx grc
	if debug >= 1:
		print "Calculating packets dropped...\n-----------------\n-----------------"
	for found in glob.glob("Outputs/pkt*"):	#Create list for output packets
		found_tgt = found.split('/')[1]			#Isolate 'pktXXXX'
		otpt_list.append(found_tgt)				#add name to array

	otpt_list.sort()						#alphabetize list for output according to string name ex['pic0','pic1'.....]
	if debug >= 1:
		print "OUTPUT LIST:",otpt_list

	for piece in glob.glob("INPUT/pkt*"):			#create list for input packets
		piece_tgt = piece.split('/')[1]			#isolate pktXXXX string for input folder pkts
		inpt_list.append(piece_tgt)					#input file name to inpt_list

	inpt_list.sort()							#alphabetize list for input from least to highest binary value
	if debug >= 1:
		print "INPUT LIST:",inpt_list
	droppedpkt = len(inpt_list) - len(otpt_list) #use length of lists to determine # of pkts dropped
	if debug >= 1:
		print"\nTOTAL NUMBER OF PACKETS DROPPED:",droppedpkt
		print"\n-----------------\n-----------------"

	###Now we have a list of packets, lets compare with BERTEST definition!!

	for target in range(len(inpt_list)):
		BERTEST(inpt_list[target],debug=-1) 				 #BERTEST uses filenames of inpt_list in order to see whihc specific pkts were dropped/received and what bit errors the have if received

	####PRINTING FINAL RESULTS OF BER TEST--------------------------------------------------------------------------------------------
	if debug >= 0:
		print"------------------------------- Final Result -------------------------------"

	droppedpkt = float(droppedpkt)/float(len(inpt_list))		#calculate % of pkts lost

	if len(otpt_list) == 0:
		if debug >= 0:
			print "No packets were successfully received!"
		pcnt_loss = 1.
	else:
		pcnt_loss = float(0)
		for datapoint in range(len(avg_bit_loss)):			#calcualte % loss rate for rcved pkts only
			pcnt_loss += avg_bit_loss[datapoint]
		pcnt_loss = pcnt_loss/float(len(otpt_list))				#FInal average of % loss rate for rcvd pkts exclusively
	if debug >= 0:
		print "Percentage of packets dropped:",droppedpkt*100
		print "Average percentage of bits lost per received packet:",pcnt_loss*100
		print "NOTE: This average percentage does not include dropped packets."

	###GRAPH data loss vs pkts rcvd
#	grph =plot(total_bit_loss,'-b')	#plot array of % of bits lost for each packet rcvd or not
#	title('Bit Error Rate vs Packet Number')	#State title to be printed on graph
#	ylabel('Percentage of bits lost (BER)')		#Print Y-axis label of plot 'grph'
#	xlabel('Packet number')						#Print x-axis label of plot 'grph'
	###save data using pickle module
	filename = 'BER.'+str(testName)+'.SNR'+str(snr)
	# Check if the filename already exists. If it does append (#) to it.
	num = 1
	filenameNew = filename + '.pickle'
	while os.path.exists(filenameNew):
		filenameNew = filename + "("+str(num)+").pickle"
		num = num + 1
	filename = filenameNew
	cPickle.dump(total_bit_loss,file(str(folder)+'/'+filename,'wb'))		#pickle module creates file in directory to be opened later
	#Open and show graph in gnome termminal so ber_test.py can continue to run
	show()							#show graph, program will continue after plot is closed

	#call(['gnome-terminal','--','./pickle_open.py']) #Opens graph for TX (TURN OFF ACTION TBD)

# if the code is called from the terminal, get input and run function.
if __name__=='__main__':
	#testName = raw_input("Please enter a test name: ")
	#folder = raw_input("Please enter a folder for the results to be saved in: ")
	#snr = raw_input("Please enter the SNR of the test: ")
	testName = '1.SNRTest.'
	folder = "simTests"
	snr = 3
	if not os.path.exists(folder):
		os.makedirs(folder)
	test(testName,snr,folder,debug=4)