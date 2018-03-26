# William "Squilliam" Lahann
# Packetize data for demod
# Sends data to udp block in GNURadio

import socket, os, re, datetime,shutil
import numpy as np
import math


class packetize():
    SUPPORTEDTYPES = [bytearray, str, list]

    def __init__(self, port=200, preamble=5):
        print("Setting up class")
        # self.port = port
        self.preamble = preamble
        self.ip = "127.0.0.1"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, data):
        ### check datatypes ###
        datatype = type(data)
        if not (type(data) in self.SUPPORTEDTYPES):
            raise TypeError("Data must be passed in as Bytearrray or string.")
        if datatype == str or datatype == list:
            # IF data was passed in not as bytearray, then adjust here
            data = bytearray(data)
        ## check lneght of pkt ###
        datalen = len(data)
        if datalen > 10000:
            raise ValueError("Size of dat too large for protocol. MUST BE LESS THAN 10,000 BYTES.")

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
        print "packet:", message
        return message

    # self.sock.sendto(message, (self.ip,self.port))

    def close(self):
        ## send EOF file ###
        self.sock.sendto('', (self.ip, self.port))
        ### close socket on python's side ###
        self.sock.close()
        self.sock.shutdown()


# Used in unpack to search through strings to find the index of the start of substrings
def strSearch(mainString,searchPhrase):
    indexs = [m.start() for m in re.finditer(searchPhrase,mainString)]
    return indexs


def unpack(GRCOutput,pktPrefix,outputLocation,delete=0,debug=0):

    # This code was writen where the file location would not be specified with a forward slash at the end.
    # This if statement removes the forward slash if it was included.
    if outputLocation[len(outputLocation)-1] == "/":
        outputLocation = outputLocation[:len(outputLocation-2)]

    if len(pktPrefix.split("/")) > 1:
        raise ValueError("prefix should not be a file path!")

    # Setup the save location for the file segments
    if delete == 0: # Don't delete the old unpacked files
        if os.path.exists(outputLocation):  # If the folder already exists, tag the time on the back so no data is deleted.
            date = datetime.datetime.now().strftime("%y-%m-%d-%H-%M")
            outputLocation = outputLocation+"-"+date
    else: # Do delete the old unpacked files
        if os.path.exists(outputLocation):  # If the folder already exists, tag the time on the back so no data is deleted.
            shutil.rmtree(outputLocation)
    outputLocation = outputLocation + "/"  # Add the forward slash for the file path.
    if debug >= 0:
        print("Files saved in: " + outputLocation)
    os.makedirs(outputLocation)


    # Load the output from the GRC file in as a string.
    rxFile = open(GRCOutput,'rb')
    rx = rxFile.read()
    rxFile.close()

    # Find the indexes in the GRC output file where the starts of the packets are found.
    pktStarts = strSearch(rx,pktPrefix)

    # Parse each packet that was received
    if debug >= 3:
        print("pktStarts: ",pktStarts)
        print("Length of pktStarts:" + str(len(pktStarts)))
    for i in range(len(pktStarts)):
        if debug >= 2:
            print("i: "+str(i))
        ind = pktStarts[i]  # This is the first index where the packet starts in the GRC file
        try:
            name = rx[ind:ind+7]  # Get the name of the file from the packet.

            # Check to make sure the packet name is not corrupt
            legalName = 1  # The packet is innocent until proven guilty (have to prove its illegal)
            if name == pktPrefix+str(9999): # We don't want to save synchronization packets, so they are illegal.
                legalName = 0
            try:
                nameNumber = name[len(pktPrefix):len(pktPrefix)+5] # Get the number suffix from the name
                int(nameNumber) # Attempt to convert the number to a integer.
            except:
                # The field that should be a number was not. This means the packet name is corrupt
                legalName = 0

            if debug >= 1:
                print("\nname: " + name)
            if debug >=3:
                print"legalName:",legalName

            #If the packet has a legal name, we unpack it.
            if legalName:  # If the packet name is legal, parse it.

                # Determine the length of the received file.
                length = 0
                for j in range(4):
                    temp = ord(rx[ind+7+j])
                    temp = temp * int(np.power(10,(3-j)))
                    length += temp
                # Validate length
                legalLength = 1
                if length >= 9999:
                    if debug >= 1:
                        print"Illegal Length. Dropping Packet."
                    legalLength = 0
                if debug >= 1:
                    print("length: "+str(length))

                if legalLength:  # if the packet length was legal, the packet and data will be saved.
                    # Grab the from the body of the packet determined based on the length
                    data = rx[ind+11:ind+11+length]
                    if debug >= 2:
                        print("Data Length: "+str(len(data)))
                    if debug >= 3:
                        print("Data Range: "+str(ind+10) + " to " + str(ind+10+length))
                    if debug >= 4:
                        print("data: "+data)

                    # Save the packet to the expected location. After this it should be set to use fileComb
                    pktSegment = open(outputLocation + name, 'wb')
                    pktSegment.write(data)
                    pktSegment.close()
            else:
                if debug >= 1:
                    print("Corrupt packet name (or sync packet). Don't save.")
        except IndexError:
            if debug >= 0:
                print("caught index error.")
                print("ind:",pktStarts[i])
            pass

    # Return the output location, since it might not match what was asked for.
    return outputLocation

if __name__=='__main__':
    print("Only unpacking functionality is supported when called from terminal.")
    # GRCOutput = raw_input("GRC Output file: ")
    # pktPrefix = raw_input("Level 2 packet prefix(file names): ")
    # outputLocation = raw_input("Folder where outputs will go: ")
    # if os.path.exists(outputLocation):
    #     delete = raw_input("Remove old outputs folder? (y/n) ")
    #     if delete == "y":
    #         delete = 1
    #     elif delete == 'n':
    #         delete = 0
    #     else:
    #         raise ValueError("Answer must be y or n")
    # else:
    #     delete = 0
    GRCOutput = 'Output'
    pktPrefix = 'pkt'
    outputLocation = 'Outputs'
    unpack(GRCOutput, pktPrefix, outputLocation, delete=1, debug=1)