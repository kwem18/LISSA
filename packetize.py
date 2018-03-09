#William "Squilliam" Lahann
#Packetize data for demod
#Sends data to udp block in GNURadio

import socket 
import numpy as np

class packetize():
	SUPPORTEDTYPES = [bytearray,str,list]
	
	def __init__(self,port= 200,preamble= '5'):
		print("Setting up class")
		#self.port = port
		self.preamble = preamble
		self.ip = "127.0.0.1"
		self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		
	def send(self,data):
		###check datatypes###
		datatype = type(data)
		if not(type(data) in self.SUPPORTEDTYPES):
			raise TypeError("Data must be passed in as Bytearrray or string.")
		if datatype == str or datatype == list:
			#IF data was passed in not as bytearray, then adjust here
			data = bytearray(data)
		##check lneght of pkt###
		datalen = len(data)
		if datalen > 10000:
			raise ValueError("Size of dat too large for protocol. MUST BE LESS THAN 10,000 BYTES.")
			
		###Create Header###
		#Length field
		lenFieldSize = 4 #length section only uses 4 bytes of overhead
			
		datlenarray = list(str(datalen))
		lenField = np.pad(datlenarray,[lenFieldSize-len(datlenarray),0],"constant",constant_values=0)
		temp = [0]*lenFieldSize
		for i in range(len(lenField)):
			if lenField[i] == '':
				lenField[i] = '0'
			temp[i] = int(lenField[i])
		header = bytearray(temp)
		
		###Creat synchronization data###
		syncdata = bytearray(list("TRASH"))
		syncdata.append(self.preamble)
		
		##Send ms over UDP to GRC### 3NOW JUST RETURN DATA
		message = syncdata + header + data
		print "packet:",message
		return message
		#self.sock.sendto(message, (self.ip,self.port))
		
	def close(self):
		##send EOF file###
		self.sock.sendto('',(self.ip, self.port))
		###close socket on python;s side###
		self.sock.close()
		self.sock.shutdown()
		
			