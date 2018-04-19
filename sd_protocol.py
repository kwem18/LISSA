# Handles the protocol aspects of the project
# Includes major functions such as prototransfer and protopack
import numpy as np
from glob import glob
from datetime import datetime
import os
import re

class fileTrack():
    # Written by William & Erick
    # handels functionality of prototransfer, protopack
    # Should be initialized with each picture sent!
    SUPPORTEDTYPES = [bytearray, str, list]

    def __init__(self,operatingDir,preamble =26530,filePrefix = 'pkt'):
        # Made by William
        # Accepts operatingDir (location that files are in
        # Accepts filePrefix (prefix of files to transmit)
        # All files starting with the prefix will be packaged.

        # Check types to avoid operating errors
        if type(operatingDir) != str:
            raise TypeError("The operating dirrectory must be specified as a string.")
        if type(filePrefix) != str:
            raise TypeError("The file prefix must be specified as a string.")

        # Check that the file path ends with a forward dash
        if operatingDir.endswith("/"):
            self.operatingDir = operatingDir            #Declare dynamic dir to self.operatingDir if slash is in place
        else:
            self.operatingDir = operatingDir + "/"

        self.preamble = int(preamble)
        self.filePrefix = filePrefix
        print("----------\noperatingdir:" + str(self.operatingDir) +"\n--------")
        # create the file list here.
        files = glob(self.operatingDir+self.filePrefix+"*")
        #print("Discovered files: " + str(files))
        self.fileList = []
        for i in range(len(files)):
            fileName = files[i].split("/")[2]
            self.fileList.append(fileName)
        print("FILE LIST:" + str(self.fileList))

    def ackInterp(self,ackLocation,delete=0):
        # Made by William
        # Interprets received Ack packets
        # Removes acknowledged files from the file list
        # Expecting packet acks to come in as a comment seperated string.
        # EG: pkt0001,pkt0002,pkt0004,pkt0006 means pkt0001, pkt0002, pkt0004 and pkt0006 were received correctly

        ackName = "op_data"

        if type(ackLocation) != str:
            raise TypeError("Ack Packet Location must be specified as a string!")

        if not ackLocation.endswith("/"):
            ackLocation = ackLocation + "/"

        ackPack = glob(ackLocation + ackName)

        if len(ackPack) == 0:
            # There were no operation packages found.
            return "No Op Pack"
        elif len(ackPack) > 1:
            # There were too amny ack files
            raise ValueError("Too many ackfiles! They should have been deleted after being parsed.")

        ackPack = ackPack[0]

        opFile = open(ackPack, "rb")
        opData = opFile.read()
        opFile.close()

        # Parse opData string as described at the start of this function
        acks = opData.split("'")

        # acks is now a list of the successfully received files.
        # Confirm that received acks are actual file names inside fileList. (if they aren't just throw them away)
        ackLen = len(acks)
        x = 0
        while x < ackLen:
            i = acks[x]
            if i in self.fileList:
                self.fileList = filter(lambda a: a != i,self.fileList)# if the ack received was in the file list, remove it from the file list so it isnt' sent again
                x += 1
            else:
                acks.remove(i) # If the ack wasn't part of the file list, it must have been corrupted, we'll just drop it and resend the file.
                ackLen += -1

        # Delete or remove the old ackPack.
        if delete == 1:
            # Delete the file after it's parsed.
            os.remove(ackLocation+ackName)
        else:
            # Rename the file after it's parsed.
            date = datetime.now().strftime("%y-%m-%d-%H-%M")
            newName = ackLocation + ackName + date
            os.rename(ackLocation+ackName, newName)

        # Determine the number of tiles to let to transmit.
        filesRemaining = len(self.fileList)

        # Returns number of packets that still need to be received.
        # Once 0 is returned, all packets were received.
        # All packets received once fileList is empty
        return filesRemaining

    def filePack(self):
        # Made by Erick Terrazas
        #NO RETURN OBJECT ONLY CREAT TX_INPUT.BIN
        # Packages the file list into a file ready for GNU Radio
        #print("CURRENT FILE LIST:" + str(self.fileList))
        l_fieldsize = 4 #size of length header (secondary)
        final_data = ''
        for pktname in self.fileList:
            tgt = open(self.operatingDir+pktname,'rb')  #Open file from dynamic dir
            payload = tgt.read()                            #Read the payload data

            ###Start creating 2ndary header-------------------------------
            #Length Header
            pyld_len = len(payload)
            fieldarray = list(str(pyld_len))        #create empty list as long as numerical value of pyld_len
            lenfield = np.pad(fieldarray,[l_fieldsize-len(fieldarray),0],"constant",constant_values=0)
            tmp = [0]*l_fieldsize
            for index in range(len(lenfield)):
                if lenfield[index] == '':
                    lenfield[index] = 0 # Changed from equal to int(lenfield[index])
                tmp[index] = int(lenfield[index])
            pkt_length_header = bytearray(tmp)      #This variable will be added with pyld(bytearray type)


            print("Creating! data: "+str(len(payload)))
            print("Creating! length: "+str(pyld_len))
            print("Creating! name: "+str(pktname))
            ### Create checksum by calling CREATE_CHECKSUM definition-------
            pkt_checksum_header = CREATE_CHECKSUM(payload,pyld_len,pktname)
            packed_pkt = pktname + pkt_length_header + pkt_checksum_header + payload
            print("Created checksum: "+str(pkt_checksum_header))

            ### add primary header
            packed_pkt = self.packetize(packed_pkt)     #pkt now has been packe with 'LISSA' protocol, ready for TX!
            final_data += packed_pkt                   #final data holds data to be inserted to GRC_tx

        #'final_data' now has each pkt appended on top of eachother (achieved after for loop is complete)

        ##Process to create trash packets (OBSELETE AS OF 4/15/18)----------------------------
        trash_pkt = "pkt9999"
        for thing in range(10):
            trash_pkt += "I BLESS THE RAINS DOWN IN AFRICA"
        trash_pkt = self.packetize(trash_pkt)       #trash pkt only has 1st layer header
        ##Trash pkt template made and defined to 'trash_pkt'-----------------------------------

        #final_data = trash_pkt + trash_pkt + trash_pkt + trash_pkt + trash_pkt + final_data
        #final_data += trash_pkt + trash_pkt + trash_pkt

        sendToGRC(final_data)   # Write the final data to the Tx_input file. GRC_TX READY TO SEND PICTURE PKTS
        return

    def opDataPack(self,message):
        # Made by Erick
        # Packages control messages into a format ready for GNU Radio
        # Probably just needs to pass the message to packetize

        #op_data is sent seperately from picture data so we don't need a secondary header
        #other than the pktname. Just add primary header and return data to be inserted into
        # TX_INPUT

        if type(message) != type('string'):
            raise TypeError('"message" parameter must be a string.')

        op_pktname = 'op_data'          #Standardized name for all operational data pkts used in software
        payload = message + message + message + message

        ###Start creating 2ndary header-------------------------------
        # Length Header
        l_fieldsize = 4
        pyld_len = len(payload)
        fieldarray = list(str(pyld_len))  # create empty list
        lenfield = np.pad(fieldarray, [l_fieldsize - len(fieldarray), 0], "constant", constant_values=0)
        tmp = [0] * l_fieldsize
        print("lenfield: "+str(lenfield))
        for index in range(len(lenfield)):
            if lenfield[index] == '':
                lenfield[index] = 0 # Changed from equal to int(lenfield[index])
            tmp[index] = int(lenfield[index])
        pkt_length_header = bytearray(tmp)  # This variable will be added with pyld(by

        pkt_checksum_header = CREATE_CHECKSUM(payload,pyld_len,op_pktname)

        packed_op_data_pkt =  op_pktname + pkt_length_header + pkt_checksum_header + payload #T
        # 2ndary header is attached to data packed_op_dat_pkt is the op_data pkt template-------------------------

        final_package = packed_op_data_pkt    #Add op_data pkt to pyld

        print("secondary header made")
        final_package = self.packetize(data=final_package)  #add primary header to relevant data
        print("Primary header made")

        ###MAKING TRASH PACKET----------------------------------------
        trash_pkt = "pkt9999"
        for h in range(10):
            trash_pkt += " I BLESS THE RAINS DOWN IN AFRICA"
        trash_pkt = self.packetize(trash_pkt)           #add 1st layer header to trash packet
         ###CREATED A TRASH PACKET TEMPLATE----------------------------------------

        final_package = final_package + final_package + final_package # SEND 3 pkts of same msg

        sendToGRC(final_package) # Write the final data to the Tx_input file. GRC_TX READY TO TX OP_DATA

    def packetize(self, data):
        # Made by William
        # Used to add header fields to data
        ### check datatypes ###
        datatype = type(data)
        if not (type(data) in self.SUPPORTEDTYPES):
            raise TypeError("Data must be passed in as Bytearrray or string.")
        if datatype == str or datatype == list:
            # IF data was passed in not as bytearray, then adjust here
            data = bytearray(data)
        ## check lneght of pkt ###
        datalen = len(data)
        if datalen > 9997:
            raise ValueError("Size of data too large for protocol. MUST BE LESS THAN 10,000 BYTES.")

        ### Create Header ###
        # Length field
        lenFieldSize = 4  # length section only uses 4 bytes of overhead

        datlenarray = list(str(datalen))
        lenField = np.pad(datlenarray, [lenFieldSize - len(datlenarray), 0], "constant", constant_values=0)
        temp = [0] * lenFieldSize
        for i in range(len(lenField)):
            if lenField[i] == '':
                lenField[i] = '0'
            temp[i] = int(lenField[i])
        header = bytearray(temp)

        ### Creat synchronization data ###
        syncdata = bytearray(list("SectionUsedForModulationSynchronization"))
        for i in range(4):
            preamblebit = (self.preamble >> (3 - i) * 8) & 0xFF
            syncdata.append(preamblebit)

        ## Send ms over UDP to GRC ### NOW JUST RETURN DATA
        message = syncdata + header + data
        return message
        # self.sock.sendto(message, (self.ip,self.port))

    def closePacket(self):
        # Made by William
        # Creates close packet to indicate to rx path GNU Radio to close
        # Works in conjunction with preamble detection block (ver. not implemented)

        # Logic based off of packetize function

        # Create synchronization data
        syncdata = bytearray(list("SectionUsedForModulationSynchronization"))
        for i in range(4):
            preamblebit = (self.preamble >> (3 - i) * 8) & 0xFF
            syncdata.append(preamblebit)

        # Force header to certain condition
        lenFieldSize = 4  # length section only uses 4 bytes of overhead
        datalen = 9998 # Length 9998 indicates GNU Radio Operation Data
        datlenarray = list(str(datalen))
        lenField = np.pad(datlenarray, [lenFieldSize - len(datlenarray), 0], "constant", constant_values=0)
        temp = [0] * lenFieldSize
        for i in range(len(lenField)):
            if lenField[i] == '':
                lenField[i] = '0'
            temp[i] = int(lenField[i])
        header = bytearray(temp)

        # Create close message
        data = "closecloseclosecloseclosecloseclosecloseclosecloseclose"

        # Create package
        message = syncdata + header + data
        return message

def opDataInterp(opMessageLocation,delete=0):
    # Made by William
    # Interpret operational messages
    # Accepts operating message folder as an input

    packetName = "op_data"

    if type(opMessageLocation) != str:
        raise TypeError("Operating Packet Location must be specified as a string!")

    if not opMessageLocation.endswith("/"):
        opMessageLocation = opMessageLocation + "/"

    opPack = glob(opMessageLocation+packetName)

    if len(opPack) == 0:
        # There were no opperation packages found.
        return "No Op Pack"
    elif len(opPack) > 1:
        # There were too many operation packages found.
        raise ValueError("There were too many operation packages found. They should be removed/renamed after being worked with.")

    opPack = opPack[0]

    opFile = open(opPack,"rb")
    opData = opFile.read()
    opFile.close()

    if len(opData) == 0:
        opMessage = "Op Pack Empty"
    elif "picReq" in opData:
        opMessage = "picReq"
    elif "pwrOff" in opData:
        opMessage = "reboot"
    elif "Arcv" in opData:
        opMessage = "All Received"
    elif "Nothing Received" in opData:
        opMessage = "Nothing Received"
    else:
        opMessage = "messageError"

    # Delete or rename the file so the next opPack can be interpreted
    if delete == 1:
        # Delete the file after it's parsed.
        os.remove(opPack)
    else:
        # Rename the file after it's parsed.
        date = datetime.now().strftime("%y-%m-%d-%H-%M")
        newName = opMessageLocation + packetName + date
        os.rename(opPack,newName)



    # Return one of the following strings
    # picture request = picReq
    return opMessage

def unpack(GRCOutput, filePrefix, operatingFolder):
    # Written by William
    # Accepts GNU Radio (Rx) Output File
    # Saves split unpacked files into operating Folder
    # Does not save duplicate files
    # Performs light error detection. Won't save files with corrupt names/lengths
    # Returns list of the received files.

    if not operatingFolder.endswith("/"):
        operatingFolder = operatingFolder + "/"

    # Load the output of the GRC File in as a string
    rxFile =open(GRCOutput,'rb')
    rx=rxFile.read()
    rxFile.close()

    pktStarts = strSearch(rx,filePrefix)  # Find the indexes where all of the packets start
    print("pktStarts: "+str(pktStarts))

    # Check all indexes and make sure they reference packet names that can exist
    pkts = dict() # Create a dictionary that holds packet data
    x = 0
    lenpktStarts = len(pktStarts)
    while x < lenpktStarts:
        i = pktStarts[x]
        try:  # Using try in case we accidently go past the length of the string.
            name = rx[i:i+7]
            legalName = True # All names innocent until proven guilty.
            if name == filePrefix+str(9999): # We don't want to save synchronization packets, so they are illegal.
                legalName = False
                print('Illegal Name: '+name)

            if legalName:
                print("Pkt name = "+name)


            l_fieldsize = 4 #size of length header (secondary)
            # Determine the length of the packet
            length = 0
            for j in range(4):
                temp = ord(rx[i + 7 + j])
                temp = temp * int(np.power(10, (3 - j)))
                length += temp

            # Validate that the length is legit
            legalLength = True # All lengths are innocent until proven guitly
            if length >= 9999:
                print("Illegal Length: "+str(length))
                legalLength = False

            if legalName and legalLength:
                data = rx[i+13:i+13+length]

            ## validation of checksum-----------------------------------------------
            receivedCheck = rx[i+11:i+13]

            legalChecksum = False  # Checksums are considered illegal until proven otherwise
            #compute checksum again
            if legalName and legalLength:
                createdCheck = CREATE_CHECKSUM(data,length,name)#call checksum function
                if createdCheck == receivedCheck:
                    print("Checksum passed for packet: "+name)
                    legalChecksum = True
                else:
                    print("Checksum FAILED for packet: "+name)

            ##checksum test concluded-----------------------------------------------
            if legalName and legalLength and legalChecksum:
                pkts[name] = data
                x += 1 # incrememnt x so we start on the next packet.
            else:
                print("Illegal Packet index: "+str(i))
                pktStarts.remove(i) # Don't save the packets that weren't legal
                lenpktStarts += -1 # Decrease the length of the packet list because one is removed now.
        except IndexError:
            pktStarts.remove(i) # If pkt i created an index error, remove it from the list, it's incomplete.
            lenpktStarts += -1 # Decrease the length of the packet list because one is removed now.
            print("Index Error!!!!")

    # Save data from the pkts dictionary
    keys = pkts.keys()
    print("Saving Packets: "+str(keys))
    for i in keys:
        fileSegment = open(operatingFolder+i,'wb')
        fileSegment.write(pkts[i])
        fileSegment.close()

    return keys

def strSearch(mainString,searchPhrase):
    # Written by William
    # Used in unpack to search through strings to find the index of the start of substrings
    indexs = [m.start() for m in re.finditer(searchPhrase,mainString)]
    return indexs

#FUNCTIONS for CHECKSUM------------------------------------------------------------------------------------------
def CREATE_CHECKSUM(pyld,len_header,pktname):  #NOTE: len_header can be either str or bytearray!
    #Written by Erick Terrazas
    HEADER_size = 2
    checksum_field = bytearray(2)
    checksum = 0
    ##Typeerror checks
    if (type(pyld) != str):
        raise TypeError('Data must be string type')
    if type(len_header) != int:
        raise TypeError('Data must be bytearray type or a string')
    if (type(pktname) != str):
        raise TypeError('filename must be in string type')

    ### First we have to add binary data of filename into checksum
    for str_byte in pktname:
        num_val = ord(str_byte)     #Take each byte and just add it to data
        checksum += num_val         #add numerical representation
        #checksum = (checksum >> 16) + (checksum & 0xFFFF)

    ### Now we have to add binary data of length into checksum
    len_header = str(len_header)
    for str_byte in len_header:
        num_val = ord(str_byte)     #Take each byte and just add it to data
        checksum += num_val         #add numerical representation
        #checksum = (checksum >> 16) + (checksum & 0xFFFF)

    ###NOw we add pyld binary data
    for pyld_byte in pyld:
        checksum += ord(pyld_byte)
        #checksum = (checksum >> 16) + (checksum & 0xFFFF)

    ###Last step, add data to empty bytearray
    checksum_field[0] = (checksum >> 8) & 0xFF
    checksum_field[1] = (checksum) & 0xFF
    return checksum_field

def sendToGRC(final_data):
    # Writen by Erick, reformated by William
    fileinput = open('TX_INPUT.bin','wb')       #binary input file created and written
    fileinput.write(final_data)
    fileinput.close()
