import sys

sys.path.insert(0, 'grc_files')  # add grc files folder to scope of python file
from GRC_Rx import *
from GRC_Tx import *
from GPIO_function import *
import fileInterfaces
import fileManip
import sd_protocol

from time import sleep
from datetime import datetime
from shutil import copyfile
import os


def testGRCs():
    try:
        gr_rx = GRC_Rx()
        gr_tx = GRC_Tx(IF_Gain=3)
    except TypeError:
        sleep(1)
        gr_rx = None
        gr_tx = None
        prepGRC()
        gr_rx = GRC_Rx()
        gr_tx = GRC_Tx(IF_Gain=3)
        sleep(1)
        gr_rx = None
        gr_tx = None


def remote(FEMlogic, power, debug=0, fem=1):
    if power > 35:
        raise ValueError("Do not exceed IF gain level of 40!")

    # Master program for remote device
    print("/////////////////////////////// ")
    print("|||| Remote Master Program |||| ")
    print('\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ ')
    print("\n")
    # Initialize hardware/GRC controls
    print("\nListening for picture request.")
    if fem == 0:
        FEMControl = GPIO_function(sync=FEMlogic)

    # Create operating directory
    operatingDir = "OperatingFile/" + "pkt" + datetime.now().strftime("%m-%d-%H:%M") + "/"
    os.mkdir(operatingDir)
    if fem == 0:
        FEMControl.ENABLE_FEM(switch=1)  # Turn on FEM path, with only ENABLE driven high, FEM is in RX Mode

    opMesssage = None
    while opMesssage != "picReq" and opMesssage != "Nothing Received":
        print("Listening for received packets.\n")
        if fem == 0:
            FEMControl.RX_FEM()
        if debug >= 1:
            print("gr_rx turning on")
        gr_receive(6000)  # Attempt to receive for 6000 seconds
        if debug >= 1:
            print("grc_rx turning off")
        # Interpret the received command
        sd_protocol.unpack("Output", filePrefix="op_data", operatingFolder=operatingDir)
        opMesssage = sd_protocol.opDataInterp(operatingDir)
        print("opMessage : " + opMesssage)
        print("operatingFolder : " + operatingDir)

    # take a pciture
    # picLocation = Camera_control.takepicture()
    picLocation = "sat_pic.JPG"
    if debug >= 2:
        print("SPLITTING PICTURE FROM DIRECTORY")

    # split the picture
    fileManip.cut(picLocation, operatingDir + "pkt", 1000)

    # Initilize the file manager
    fileManager = sd_protocol.fileTrack(operatingDir, preamble='26530', filePrefix='pkt')

    filesRemaining = 10  # Set the files remaining above 0 so we enter the loop. an actual value will be set inside the loop
    while filesRemaining > 0:
        # Create a packet file to call against gnu radio
        fileManager.filePack()
        print("filesRemaining after filepack iteration:" + str(filesRemaining))
        # Transmit the packet file
        if fem == 0:
            FEMControl.TX_FEM()
        print("+=+=+=+=+=+=+=\ngr_transmit starting\n+=+=+=+=+=+=+=\n")
        gr_transmit(power, 20)  # Transmit the picture data for 20 seconds
        print("+=+=+=+=+=+=+=\ngr_transmit finished\n+=+=+=+=+=+=+=")
        # Wait for the ackpack
        if fem == 0:
            FEMControl.RX_FEM()
        if debug >= 1:
            print("Starting GRC Receive")
        gr_receive(40)  # Attempt to receive status packets for 40 seconds.
        if debug >= 2:
            print("gr_rx has stopped")
        # Unpack the ackPack
        if debug >= 0:
            print("unpacking data using 'unpack' definition")
        sd_protocol.unpack("Output", "op_data", operatingDir)

        # Interpret the ackPack
        filesRemaining = fileManager.ackInterp(operatingDir)

    print("Picture successfully transmitted.")
    fileManager.opDataPack("Arcv")

    opMesssage = None
    while opMesssage != "All Received":
        # fileManager.opDataPack("Tx Done") #DELETE IF NOT USED FOR FULL-sys TEST
        if fem == 0:
            FEMControl.TX_FEM()
        if debug >= 0:
            print("gr_tx is sending operational data of 'Tx'_done")
        gr_transmit(power, 15)  # Send the all done message for 10 seconds
        if fem == 0:
            FEMControl.RX_FEM()
        if debug >= 0:
            print("gr_rx is listening to operational data.")
        gr_receive(40)
        sd_protocol.unpack("Output","op_data",operatingDir)
        opMesssage = fileManager.ackInterp(operatingDir)
        print ("Op message received: "+str(opMesssage))

    print("All done!")
    ### SHUTDONW BELOW WAS ADDED BY ERICK
    if fem == 0:
        FEMControl.shutdown()


def host(FEMlogic, power, userinput=1, debug=0, fem=0):
    if power > 35:
        raise ValueError("Do not exceed IF gain level of 40!")

    # Master program for server device
    print("/////////////////////////////// ")
    print("||||| Host Master Program ||||| ")
    print('\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ ')

    if fem == 0:
        FEMControl = GPIO_function(sync=FEMlogic)

    if userinput == 1:
        raw_input("Send Picture Request? (remote node must be running.) [enter]")

    if debug >= 0:
        print("Requesting picture.")

    # Create operating directory
    operatingDir = "OperatingFile/" + "pkts" + datetime.now().strftime("%m-%d-%H:%M") + "/"
    os.mkdir(operatingDir)
    if debug >= 2:
        print("Created operating dirrectory as : " + str(operatingDir))

    # Create file manager object
    fileManager = sd_protocol.fileTrack(operatingDir, preamble=26530, filePrefix='pkt')
    if debug >= 2:
        print("Initilized fileTrack.")

    if debug >= 2:
        print("Getting ready to send picture request.")
    # Package picture request for transmission
    fileManager.opDataPack("picReq")

    if fem == 0:
        FEMControl.ENABLE_FEM(switch=1)

    # Run GRC TX to send the opPack
    if debug >= 0:
        print("Transmitting Picture Request")
    if fem == 0:
        FEMControl.TX_FEM()
    gr_transmit(power, 10)  # Transmit picture request for 10 seconds
    if debug >= 1:
        print("Finished transmitting picture request")

    receivedFiles = []
    while receivedFiles != "All Received":
        # Run GRC Rx to listen for the picture to come back
        if debug >= 1:
            print("Waiting to receive data packages")
        if fem == 0:
            FEMControl.RX_FEM()
        gr_receive(40)  # Attempt to receive picture response for 40 seconds
        if debug >= 1:
            print("Finished receiving file.")

        # Unpack the received files
        if debug >= 1:
            print("Unpacking files.")
        receivedFiles = sd_protocol.unpack("Output", "pkt", operatingDir)  # unpack received files to operating dir
        if receivedFiles == []:  # No files received with pkt header
            if debug >= 2:
                print("Didn't find any data packets. Checking for Op Data.")
            # Try to unpack op_data instead
            receivedFiles = sd_protocol.unpack("Output", "op_data",
                                               operatingDir)  # unpack received files to operating dir
            if receivedFiles != []:
                # An op_data packet was received
                if debug >= 1:
                    print("Found opdata!")
                receivedFiles = sd_protocol.opDataInterp(operatingDir)  # Interpret op_data
                print("Op Data: " + receivedFiles)
                if receivedFiles == "All Received":
                    break
            else:
                fileManager.opDataPack("Nrcv")
        else:
            # Reply with ack pack of received files
            fileManager.opDataPack(str(receivedFiles))
        if debug >= 0:
            print("Transmitting status packet")
        if fem == 0:
            FEMControl.TX_FEM()
        gr_transmit(power, 15)  # Transmit status picture for 15 seconds

    if debug >= 0:
        print("All Packets Received!")

    fileManager.opDataPack("Arcv")
    if fem == 0:
        FEMControl.TX_FEM()
    if debug >= 0:
        print("Transmitting reply to all done.")
    gr_transmit(power,15)
    if fem == 0:
        FEMControl.RX_FEM()
    if debug >= 0:
        print("All done, shutting down.")
    if fem == 0:
        FEMControl.ENABLE_FEM(switch=0)
        FEMControl.shutdown()

    # Combine the packets into a pictures.
    pictureName = "picture" + datetime.now().strftime("%m-%d-%H:%M") + ".jpg"
    fileManip.comb(operatingDir + "pkt", pictureName)

    print("File Received, All done.")

    ###ADDED BY ERICK T
    if fem == 0:
        FEMControl.shutdown()


def gr_transmit(power, runTime):
    sleep(5)
    gr_tx = GRC_Tx(IF_Gain=power)
    gr_tx.start()  # start the transmit path
    sleep(runTime)
    gr_tx.stop()  # wait for the transmit path to finish
    sleep(1)
    gr_tx = None


def gr_receive(runTime):
    gr_rx = GRC_Rx()
    gr_rx.start()  # start the transmit path
    fileInterfaces.watchFile("Output", changeHold=5, interval=500, stopAfter=runTime)
    gr_rx.stop()  # wait for the transmit path to finish
    sleep(1)
    gr_rx = None


def prepGRC():
    # Called to prepare the grc python files.
    # Restors python top block file for GRC file control
    # This will need to be called after every time the GRC files are run not through python

    # Remove the wrong top block python files.
    os.remove("grc_files/GRC_Rx.py")
    os.remove("grc_files/GRC_Tx.py")

    # Copy in the saved, callable, python files.
    copyfile("GRC_Rx_Callable.py", "grc_files/GRC_Rx.py")
    copyfile("GRC_Tx_Callable.py", "grc_files/GRC_Tx.py")


if False:
    if __name__ == "__main__":
        sequential = raw_input("Is this device using the sequential logic FEM control board? ([Y]es/[N]o) ")
        if 'y' in sequential or 'Y' in sequential:
            logic = 0
        elif 'n' in sequential or 'N' in sequential:
            logic = 1
        else:
            raise ValueError("Input must be specified as [Y]es or [N]o.")

        power = raw_input("What IF Gain value should the SDR transmit at? (integer): ")
        try:
            power = int(power)
        except ValueError:
            raise TypeError("The Gain value must be specified as an integer.")

        remote_or_host = raw_input("Is this controlling the remote or host device? ([R]emote/[H]ost): ")

        debugLevel = raw_input("What level of debug would you like to run? -1 to 5? ")

        # Make sure the GRC's can be called.
        testGRCs()

        if "R" in remote_or_host or "r" in remote_or_host:
            remote(logic, power, debug=debugLevel, fem=FEM_sw)
        elif "H" in remote_or_host or "h" in remote_or_host:
            host(logic, power, debug=debugLevel, fem=FEM_sw)
        else:
            raise ValueError("Input must be specified as [H]ost or [R]emote.")

if __name__ == "__main__":
    logic = 0
    power = 20
    debugLevel = 5
    FEM_sw = 0

    # testGRCs()

    remote_or_host = raw_input("Is this controlling the remote or host device? ([R]emote/[H]ost): ")
    if "R" in remote_or_host or "r" in remote_or_host:
        remote(logic, power, debug=debugLevel, fem=FEM_sw)
    elif "H" in remote_or_host or "h" in remote_or_host:
        host(logic, power, debug=debugLevel, fem=FEM_sw)
    else:
        raise ValueError("Input must be specified as [H]ost or [R]emote.")
