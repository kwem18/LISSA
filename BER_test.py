#BER TEST Erick Terrazas G00776650
#Last edit made on 3/24/18

#NOTES: THis program needs BER_samp.bin, and the received bin file from GRC_RX 
from subprocess import call		#For gnome terminal call cmd
from pathlib import Path
from matplotlib.pyplot import *		#FOr data gathering
from decimal import *				#for percentage calcuation
import os
import sys
import time
import glob
import cPickle			#same as pickle module but allegedyly "1000 times faster"

avg_bit_loss = []		#glbl var list avg bits lost for only rcvd pkts
total_bit_loss = []     #percentage of bits lost for every pkt including dropped pkts
#------------------------------------------------------------------------------------------------------------------------------------
def BERTEST(filename_in):
	global avg_bit_loss
	global total_bit_loss
	file = str(filename_in)				#INPUT FILENAME MUST BE PUT IN HERE
	filecheck0= "INPUT/" + file			#Path of input pkt at INPUT folder of directory
	filecheck1 = "OUTPUT/"+ file		#Path of POSSIBLE received packet at OUTPUT folder of directory
	print "BERTEST for packet:",file	#State the name of pkt we are hecking for inconsistencies with test pkt
	fpath0 = Path(filecheck0)					#designates the path of input filename with respect to main directory
	fpath = Path(filecheck1)				#designates the path of output filename with respect to main directory
	
	if (fpath0.is_file() & fpath.is_file()):
		print "/////////////////////////////////////////////////////////////////////////////\nPACKET exists for:",file
		print "\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n"
			  
		
	else:
		total_bit_loss.append(Decimal(1))  #acknowledge 100% which implies lost pkt for plot graph of %bitloss vs pktnumber
		print "\n##############################\nPACKET DROPPED for:",file
		print "##############################\n"
		print "-----------------------------------------------------------------------------#\n"
		return
		
	f = open(filecheck0,'rb')					#ACESS TEST FILE in INPTU FOLDER
	h = open(filecheck1,'rb')					#ACCESS FILE in OUTPUT FOLDER
	switch = 1
	counter = 7
	input_list = []					#list in order to indicate byte and bit location of data
	output_list = []				#list output for byte and bit location of data
	bit_error_count = 0				#define bit error count for packet
	while(switch==1):				#while loop used in order to read a byte for input & output and place them into their respective lists
		counter = 7
		beta = f.read(1)			#beta holds byte read from input pkt
		beta1 = h.read(1)			#beta1 holds byte read from output pkt
		if beta:
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
        
			input_list.append(byte_list)		#append byte_list into input_list ex (byte_list = [ [0,0,0,1,0,1,0,0] , [0,0,0,0,0,0,0,0] , ... ])
			output_list.append(byte_list1)
		else:
			switch = 0
			break
	f.close()
	h.close()
	bit_error_count = 0							 #counter for number of bit inconsistencies
	for x in range(len(input_list)):					#for loop uses x at byte value, and y as bit number 
		for y in range(len(input_list[0])):
			if input_list[x][y] == output_list[x][y]:		#Nothing happens if bit locations from both lists are the same
				continue
			else:											#difference in bit value leads to acknowledgment of a bi error
				bit_error_count += 1
				print "Bit error at byte",x
				print "at bit number", y
				print "INPUT  BYTE:",input_list[x]			#show byte where error occurred
				print "OUTPUT BYTE:",output_list[x]
				print "\n------------------------------------------------"
	pkt_bit_loss = Decimal(bit_error_count)/Decimal(len(input_list)*8)
	avg_bit_loss.append(pkt_bit_loss) 			#Add percentage loss to grand list, will divide by existing pkts later in main function
	total_bit_loss.append(pkt_bit_loss) 		#Add percentage to grand total for plot
	print "Percentage of bits lost:",pkt_bit_loss		#Print BER for pkt being checked at the the time of defintion being used
	print "\nEND BERTEST OF:",file
	print "\n-----------------------------------------------------------------------------#\n"
	return 	#Leave definition		
	
	
#MAIN FUNCTION--------------------------------------------------------------------------------------------------------------------------
#########################################################################################################################################

###PACKETS DROPPED CHECK START
###WE first strip secondary header of of GR_rx output binary file
#We create an output pkt and store it into the OUTPUT folder, this process ends at line 139
print "Stripping output packets out of file and into OUTPUT folder\n-----------------\n-----------------\n-----------------"
outputf = open("OUTPUT",'rb')		#open grc output_list.  
lever = 1 
									#For while loop
while(lever==1):
	length = 0
	name = outputf.read(7)					#read pkt name save it to variable 'name'
	if name:
		alpha = outputf.read(1)			#read length based on int value of each byte
		if (not alpha) or len(alpha)==0:
			print "\nlength of payload < field length value, escaping definition.\n"
			lever = 0
			break
		length += (ord(alpha)*1000)
		alpha = outputf.read(1)
		if (not alpha) or len(alpha)==0:
			print "\nlength of payload < field length value, escaping definition.\n"
			lever = 0
			break
		length += (ord(alpha)*100)
		alpha = outputf.read(1)
		if (not alpha) or len(alpha)==0:
			print "\nlength of payload < field length value, escaping definition.\n"
			lever = 0
			break
		length += (ord(alpha)*10)
		alpha = outputf.read(1)
		if (not alpha) or len(alpha)==0:
			print "\nlength of payload < field length value, escaping definition.\n"
			lever = 0
			break
		length += ord(alpha)					#length calculated
		
		msg = outputf.read(length)			#get payload
		r = open("OUTPUT/"+name,'wb')		#make new file at OUTPUT folder using name
		r.write(msg)						#put payload into new file	
		r.close() 							#close file
	else:
		print "DIDN'T READ DATA! ESCAPING DEFINITION
		outputf.close()
		lever = 0
		break
print "OUT pkts now in OUTPUT folder\n----------\n----------\n----------"
###NOW we have an input segment in main dir., and its corresponding input in OUTPUT folder
#-We have to make a list of both file groups to calculate files dropped\n------------------------------------
otpt_list = []		#This list will have the filenames of packets we outputted from Rx grc
inpt_list = []		#This list will have the filenames of packets we inputted into Tx grc
print "Calculating packets dropped...\n-----------------\n-----------------"
for found in glob.glob("OUTPUT/pkt*"):	#Create list for output packets
	found_tgt = found.split('/')[1]			#Isolate 'pktXXXX'
	otpt_list.append(found_tgt)				#add name to array

otpt_list.sort()						#alphabetize list for output according to string name ex['pic0','pic1'.....]
print "OUTPUT LIST:",otpt_list	

for piece in glob.glob("INPUT/pkt*"):			#create list for input packets
	piece_tgt = piece.splt('/')[1]			#isolate pktXXXX string for input folder pkts
	inpt_list.append(piece)					#input file name to inpt_list
	
inpt_list.sort()							#alphabetize list for input from least to highest binary value
print "INPUT LIST:",inpt_list
droppedpkt = len(inpt_list) - len(otpt_list) #use length of lists to determine # of pkts dropped

print"\nTOTAL NUMBER OF PACKETS DROPPED:",droppedpkt
print"\n-----------------\n-----------------"
	
###Now we have a list of packets, lets compare!

for target in range(len(inpt_list)):
	BERTEST(inpt_list[target])  #BERTEST uses filenames of inpt_list in order to see whihc specific pkts were dropped/received and what bit errors the have if received
	
####PRINTING FINAL RESULTS OF BER TEST--------------------------------------------------------------------------------------------
print "\n---FINAL RESULTS---\n"

droppedpkt = Decimal(droppedpkt)/Decimal(len(inpt_list))		#calculate % of pkts lost

#droppedpkt = droppedpkt/len(inpt_list)
pcnt_loss = Decimal(0)
for datapoint in range(len(avg_bit_loss)):			#calcualte % loss rate for rcved pkts only
	pcnt_loss += avg_bit_loss[datapoint]
pcnt_loss = pcnt_loss/Decimal(len(otpt_list))				#FInal average of % loss rate for rcvd pkts exclusively
print "Percentage of packets dropped:",droppedpkt*100
print "Average percentage of bits lost per received packet:",pcnt_loss*100
print "\nNOTE: This average percentage does not include dropped packets.\n"

###GRAPH data loss vs pkts rcvd
grph =plot(total_bit_loss,'-b')	#plot array of % of bits lost for each packet rcvd or not
title('Bit Error Rate vs Packet Number')	#State title to be printed on graph
ylabel('Percentage of bits lost (BER)')		#Print Y-axis label of plot 'grph'
xlabel('Packet number')						#Print x-axis label of plot 'grph'
###save grpah using pickle module
#graphfilename = 'BERplot.pickle'
#cPickle.dump(grph,file(graphfilename,'wb'))		#pickle module creates file in directory to be opened later
#Open and show graph in gnome termminal so ber_test.py can continue to run
show()							#show graph, program will continue after plot is closed

#call(['gnome-terminal','--','./pickle_open.py']) #Opens graph for TX (TURN OFF ACTION TBD)


print "\nEND TEST\n-----------------------------------------------------"
