import sys
sys.path.insert(0,'grc_files')
import All_One_Comp
import packetize
import BER_test
import numpy as np
from time import time
from time import sleep
from datetime import datetime
import os
import GPIO_function

def main(powers,repetitions,folder):
    esttimePerTest = 60 # Seconds
    numOfTests = len(powers) * repetitions
    totalTime = esttimePerTest * numOfTests
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!!!!!! THIS MUST BE THE COMPUTER USED FOR RECEIVING !!!!!!!")
    print("! Pkts that will be transmitted must be in 'inputs' folder !")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    print"\n\nStarting Automated Tests."
    print"Testing",len(powers),"different Power levels through",repetitions,"repetitions."
    print"Expected individual test time of",esttimePerTest,'seconds.'
    print"Expected total test time of",totalTime/60.,"minutes. (",totalTime/3600.,"hours)\n\n"
    runTest = raw_input("Are you sure you want to run this test. (y/n): ")
    if runTest != "y":
        return
    FEMCONTROL = GPIO_function.GPIO_function(sync=0)
    FEMCONTROL.ENABLE_FEM(switch=1)
    FEMCONTROL.RX_FEM()

    startTime = time()

    curTest = 1
    for i in range(1, repetitions + 1):
        testName = str(i) + ".PowerTest"
        for j in powers:
            print"--------------------- Waiting for the start of the next minute ---------------------"
            wait_for_minute(0.01) # Check for the start of the next minute at an interval of 10ms

            testTime = time()
            print"---------------------- Interation:", i, " Power Level:", j, '-----------------------'

            failed = 0
            success = 0
            while failed <= 2 and success != 1:
                try:
                    print("Running GNU Radio")
                    grc = All_One_Comp.All_One_Comp()
                    grc.start()
                    success = 1
                except RuntimeError as e:
                    print("\n---- Whoa, caught an error when starting GNU Radio! ----\n")
                    print e
                    print("\n---- That'll mess up the timing of the tests... ----\n")
                    sleep(1)
                    grc = None
                    failed += 1

            if success != 1:
                print("Test canelced because of percistant errors.")
            else:
                print("Waiting for test to finish")
                sleep(45)

                grc.stop()

                print("Instructed GRC to stop")
                sleep(1)

                print("Closing GRC")
                grc = None
                print("Running Packetize")
                packetize.unpack("Output", "pkt", "Outputs", delete=1, debug=-1)

                print("Running BER Test")
                BER_test.test(testName, j, folder, debug=0)

                ## Generate status report
                print"------------------------------ Testing Status ------------------------------"
                print"Finished Test Number:", curTest, "of", numOfTests, 'total.'
                print"Test time:", time() - testTime, 'seconds'
                print"Elapsed Time:", (time() - startTime) / 60., 'minutes (', (time() - startTime) / 3600., 'hours)'

            remaining = (numOfTests - curTest) * (
            (time() - startTime) / curTest)  # number of test remaining times average time per test so far.
            print"Estimated Time Remaining:", remaining / 60., "minutes (", remaining / 3600., 'hours)'
            print"----------------------------------------------------------------------------\n\n"
            curTest = curTest + 1
    FEMCONTROL.shutdown()

def wait_for_minute(checkRate):
    # Effectively waits for the start of the next minute.
    # Function will hold the program calling program until the next minute.
    # Checks for the start of the next minute at a rate of 'checkRate'

    original = int(time()) / 60
    dif = False
    while not dif:
        current = int(time()) / 60
        if original != current:
            dif = True
        else:
            sleep(checkRate)


if __name__ == '__main__':
    highPower = 45
    lowPower = 3
    powerLevels = 15
    repetitions = 5
    topFolder = 'SplitSystemTests'

    folder = topFolder + '/' + datetime.now().strftime("%m-%d-%H:%M")
    os.makedirs(folder)
    powers = np.linspace(lowPower, highPower, powerLevels)
    main(powers, repetitions, folder)
