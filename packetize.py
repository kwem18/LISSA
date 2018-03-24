# William "Squilliam" Lahann
# Packetize data for demod
# Sends data to udp block in GNURadio

import socket
import numpy as np


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

def unpack(GRCOutput,pktPrefix,outputLocation):

    # This code was writen where the file location would not be specified with a forward slash at the end.
    # This if statement removes the forward slash if it was included.
    if outputLocation[len(outputLocation-1)] == "/":
        outputLocation = outputLocation[:len(outputLocation-2)]

    if len(split(prefix,"/")) > 1:
        raise ValueError("prefix should not be a file path!")

    # Setup the save location for the file segments
    if os.path.exists(outputLocation):  # If the folder already exists, tag the time on the back so no data is deleted.
        date = datetime.datetime.now().strftime("%y-%m-%d-%H-%M")
        outputLocation = outputLocation+"-"+date
        print("Files saved in: " + outputLocation)
    outputLocation = outputLocation + "/"  # Add the forward slash for the file path.
    os.makedirs(outputLocation)

    # Load the output from the GRC file in as a string.
    rxFile = open(GRCOutput,'rb')
    rx = rxFile.read()
    rxFile.close()

    # Find the indexes in the GRC output file where the starts of the packets are found.
    pktStarts = strSearch(rx,pktPrefix)

    # Parse each packet that was received
    for i in range(len(pktStarts)):
        ind = pktStarts[i]  # This is the first index where the packet starts in the GRC file
        name = rx[ind:ind+7]  # Get the name of the file from the packet.
        if name != filePrefix+str(9999):  # packets 9999 are used for syncronization and not saved.
            # Determine the length of the received file.
            length = 0
            for j in range(4):
                temp = ord(rx[ind+7+j])
                temp = temp * int(np.power(10,(3-j)))
                length += temp
            # Grab the from the body of the packet determined based on the length
            data = rx[ind+10:ind+10+length]
            if debug >= 1:
                print("\nname: "+name)
                print("length: "+str(length))
                print("Data Length: "+str(len(data)))
                print("data: "+data)

            # Save the packet to the expected location. After this it should be set to use fileComb
            pktSegment = open(outputLocation+name,'wb')
            pktSegment.write(data)
            pktSegment.close()
        else:
            print("Sync packet. Don't save.")
            
    # Return the output location, since it might not match what was asked for.
    return outputLocation
