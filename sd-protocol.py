# Handles the protocol aspects of the project
# Includes major functions such as prototransfer and protopack

from glob import glob
from datetime import datetime
import os

class fileTrack():
    # Written by William & Erick
    # handels functionality of prototransfer, protopack
    # Should be initialized with each picture sent!
    SUPPORTEDTYPES = [bytearray, str, list]

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

        self.preamble = preamble
        self.filePrefix = filePrefix

        # create the file list here.
        files = glob(self.operatingDir+self.filePrefix)

        self.fileList = []
        for i in len(files):
            fileName = files[i].split("/")[1]
            self.fileList.append(fileName)


    def ackInterp(self,ackLocation,delete=0):
        # Made by William
        # Interprets received Ack packets
        # Removes acknowledged files from the file list
        # Expecting packet acks to come in as a comment seperated string.
        # EG: pkt0001,pkt0002,pkt0004,pkt0006 means pkt0001, pkt0002, pkt0004 and pkt0006 were received correctly

        ackName = "ackPack"

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

        opFile = open(ackPack, "rb")
        opData = opFile.read()
        opFile.close()

        # Parse opData string as described at the start of this function
        acks = opData.split(",")

        # acks is now a list of the successfully received files.
        # Confirm that received acks are actual file names inside fileList. (if they aren't just throw them away)
        for i in acks:
            if not i in self.fileList:
                acks.remove(i) # If the ack wasn't part of the file list, it must have been corrupted, we'll just drop it and resend the file.

        # need to subtract acks from the fileList, so they aren't sent again.
        self.fileList =list(set(self.fileList)^set(acks)) # Removes all acks from the file list.

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
        # Made by Erick
        # Packages the file list into a file ready for GNU Radio
        self.fileList

    def opDataPack(self,message):
        # Made by Erick
        # Packages control messages into a format ready for GNU Radio
        # Probably just needs to pass the message to packetize

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

    opFile = open(opPack,"rb")
    opData = opFile.read()
    opFile.close()

    if len(opData) == 0:
        opMessage = "Op Pack Empty"
    elif opData == "Send Picture"
        opMessage = "picReq"
    elif opData == "powerOff"
        opMessage = "reboot"
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