import sys
sys.path.insert(0,'grc_files') # add grc files folder to scope of python file
import GRC_Rx, GRC_Tx
import fileInterfaces
import fileManip
import GPIO_function
import sd_protocol

from datetime import datetime
from shutil import copyfile
import os

def testGRCs():
    try:
        gr_rx = grc_rx()
        gr_tx = grc_tx(IF_Gain=power)
    except TypeError as e:
        if str(e) == "__init__() takes exactly 1 argument (2 given)":
            prepGRC()
        else:
            print("!!! GRC files failed test and were not able to be automatically corrected !!!")
            raise


def remote(FEMlogic,power):
    # Master program for remote device
    print("/////////////////////////////// ")
    print("|||| Remote Master Program |||| ")
    print('\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ ')

    # Initialize hardware/GRC controls
    print("Listening for picture request.")
    gr_rx = grc_rx()
    gr_tx = grc_tx(IF_Gain=power)
    FEMControl = GPIO_function(sync=FEMlogic)

    # Create operating directory
    operatingDir = "pkts"+datetime.now().strftime("%m-%d-%H:%M")+"/"
    os.mkdir(operatingDir)

    FEMControl.ENABLE_FEM(switch=1)     #Turn on FEM path, with only ENABLE driven high, FEM is in RX Mode

    print("Listening for received packets.")
    FEMControl.RX_FEM()
    gr_rx.start()  # start the receive path
    fileInterfaces.watchFile("Output", changeHold=5, interval=500) # stays in function till file change detected.
    gr_rx.stop()  # Stop the receive path after the Output file wasn't changed for 2500ms

    # Interpret the received command
    sd_protocol.unpack("Output",filePrefix="op_data",operatingFolder=operatingDir)
    opMesssage = sd_protocol.opDataInterp(operatingDir)

    if opMesssage == "picReq":
        # take a picture
        picLocation = Camera_control.takepicture()

        #split the picture
        fileManip.cut(operatingDir+"pkt",picLocation,1000)

        # Initilize the file manager
        fileManager = sd_protocol.fileTrack(operatingDir, preamble='26530',filePrefix='pkt')

        filesRemaining = 10 # Set the files remaining above 0 so we enter the loop. an actual value will be set inside the loop
        while filesRemaining > 0:
            # Create a packet file to call against gnu radio
            fileManager.filePack()

            # Transmit the packet file
            FEMControl.TX_FEM()
            gr_tx.start()
            gr_tx.wait()

            # Wait for the ackpack
            FEMControl.RX_FEM()
            gr_rx.start()
            fileInterfaces.watchFile("Output", changeHold=5,
                                     interval=500)  # stays in function till file change detected.
            gr_rx.stop()  # Stop the receive path after the Output file wasn't changed for 2500ms

            # Unpack the ackPack
            sd_protocol.unpack("Output","op_data",operatingDir)

            # Interpret the ackPack
            filesRemaining = fileManager.ackInterp(operatingDir)

        print("Picture successfully transmitted.")

        fileManager.opDataPack("Tx Done")

        FEMControl.TX_FEM()
        gr_tx.start()
        gr_tx.wait()

        print("All done!")
        ###SHUTDONW BELOW WAS ADDED BY ERICK
        FEMControl.shutdown()


def host(FEMlogic,power,userinput = 1):
    # Master program for server device
    print("/////////////////////////////// ")
    print("||||| Host Master Program ||||| ")
    print('\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ ')

    #Initiate GNU Radio Files
    gr_rx = grc_rx()
    gr_tx = grc_tx(IF_Gain = power)
    FEMControl = GPIO_function(sync = FEMlogic)

    if userinput == 1:
        raw_input("Send Picture Request? (remote node must be running.) [enter]")
    else:
        print("Requesting picture.")

    # Create operating directory
    operatingDir = "pkts"+datetime.now().strftime("%m-%d-%H:%M")+"/"
    os.mkdir(operatingDir)

    # Create file manager object
    fileManager = sd_protocol.fileTrack(operatingDir,preamble="26530",filePrefix='pkt')

    # Package picture request for transmission
    fileManager.opDataPack("Send Picture")

    FEMControl.ENABLE_FEM(switch=1)

    # Run GRC TX to send the opPack
    print("Transmitting Picture Request")
    FEMControl.TX_FEM()
    gr_tx.start() # start the transmit path
    gr_tx.wait() # wait for the transmit path to finish

    receivedFiles = []
    while receivedFiles != "All Received":
        # Run GRC Rx to listen for the picture to come back
        print("Waiting to receive data packages")
        FEMControl.RX_FEM()
        gr_rx.start()  # start the receive path
        fileInterfaces.watchFile("Output",changeHold=5,interval=500)
        gr_rx.stop() # Stop the receive path after the Output file wasn't changed for 2500ms

        # Unpack the received files
        receivedFiles = sd_protocol.unpack("Output","pkt",operatingDir)# unpack received files to operating dir
        if receivedFiles == []: # No files received with pkt header
            # Try to unpack op_data instead
            receivedFiles = sd_protocol.unpack("Output", "op_data", operatingDir)  # unpack received files to operating dir
            if receivedFiles != []:
                # An op_data packet was received
                receivedFiles = sd_protocol.opDataInterp(operatingDir) # Interpret op_data

        # Reply with ack pack of received files
        fileManager.opDataPack(receivedFiles)
        print("Transmitting ack pack")
        FEMControl.TX_FEM()
        gr_tx.start()
        gr_tx.wait()

    print("All Packets Received!")
    FEMControl.ENABLE_FEM(switch=0)
    FEMControl.shutdown()

    # Combine the packets into a pictures.
    pictureName = "picture"+datetime.now().strftime("%m-%d-%H:%M")
    fileManip.comb(operatingDir+"pkt",pictureName)

    print("File Received, All done.")

    ###ADDED BY ERICK T
    FEMControl.shutdown()


def prepGRC():
    # Called to prepare the grc python files.
    # Restors python top block file for GRC file control
    # This will need to be called after every time the GRC files are run not through python

    # Remove the wrong top block python files.
    os.remove("grc_files/GRC_Rx.py")
    os.remove("grc_files/GRC_Tx.py")

    # Copy in the saved, callable, python files.
    copyfile("GRC_Rx_Callable.py", "grc_files/GRC_Rx.py")
    copyfile("GRC_Tx_Callable.py","grc_files/GRC_Tx.py")



if __name__ == "__main__":
    sequential = raw_input("Is this device using the sequential logic FEM control board? ([Y]es/[N]o) ")
    if 'y' in sequential or 'Y' in sequential:
        logic = 0
    elif 'n' in sequential or 'N' in sequential:
        logic = 1
    else:
        raise ValueError("Input must be specified as [Y]es or [N]o.")

    power = raw_input("What IF Gain value should the SDR transmit at? (integer): ")
    if type(power) != int:
        raise TypeError("The Gain value must be specified as an integer.")

    remote_or_host = raw_input("Is this controlling the remote or host device? (Remote/Host): ")

    # Make sure the GRC's can be called.
    testGRCs()

    if "R" in remote_or_host or "r" in remote_or_host:
        remote(logic,power)
    elif "H" in remote_or_host or "h" in remote_or_host:
        host(logic,power)
    else:
        raise ValueError("Input must be specified as [H]ost or [R]emote.")
