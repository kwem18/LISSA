# Handles the protocol aspects of the project
# Includes major functions such as prototransfer and protopack

from glob import glob

class fileTrack():
    # Written by William & Erick
    # handels functionality of prototransfer, protopack
    # Should be initialized with each picture sent!

    def __init__(self,operatingDir,preamble ='26530',filePrefix = 'pkt'):
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
            self.operatingDir = operatingDir
        else:
            self.operatingDir = operatingDir + "/"

        self.filePrefix = filePrefix

        # create the file list here.
        files = glob(self.operatingDir+self.filePrefix)

        self.fileList = []
        for i in len(files):
            fileName = files[i].split("/")[1]
            self.fileList.append(fileName)

        self.preamble = preamble


    def ackInterp(self,ackLocation):
        # Made by William
        # Interprets received Ack packets
        # Removes acknolaged files from the file list
        self.fileList

        # Returns 0 if not all packets are received
        # Returns 1 once all packets were received
        # All packets receieved once fileList is empty
        return allReceived

    def filePack(self):
        # Made by Erick
        # Packages the file list into a file ready for GNU Radio
        self.fileList

    def opDataPack(self,message):
        # Made by Erick
        # Packages control messages into a format ready for GNU Radio

    def packetize(self, data):
        # Used to add header fields to data
        ###check datatypes###
        datatype = type(data)
        if not (type(data) in self.SUPPORTEDTYPES):
            raise TypeError("Data must be passed in as Bytearrray or string.")
        if datatype == str or datatype == list:
            # IF data was passed in not as bytearray, then adjust here
            data = bytearray(data)
        ##check lneght of pkt###
        datalen = len(data)
        if datalen > 9999:
            raise ValueError("Size of dat too large for protocol. MUST BE LESS THAN 10,000 BYTES.")

        ###Create Header###
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

        ###Creat synchronization data###
        syncdata = bytearray(list("TRASH"))
        syncdata.append(self.preamble)

        ##Send ms over UDP to GRC### 3NOW JUST RETURN DATA
        message = syncdata + header + data
        print "packet:", message
        return message
        # self.sock.sendto(message, (self.ip,self.port))

def opDataInterp(opMessageLocation):
    # Made by William
    # Interpret operational messages
    # Accepts operating message as an input

    # Return one of the following strings
    # picture request = picReq
    return opMessage


class packetize():
    SUPPORTEDTYPES = [bytearray, str, list]

    def __init__(self, preamble='26530'):
        print("Setting up class")
        self.preamble = preamble

