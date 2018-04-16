import sys
sys.path.insert(0,'grc_files')
import All_One_Comp
import packetize
import BER_test
import numpy as np
from time import time
from datetime import datetime
import os


def main(snr,repetitions,folder):
    timePerTest = 35 # Seconds
    numOfTests = len(snr) * repetitions
    totalTime = timePerTest * numOfTests
    print"\n\nStarting Automated Tests."
    print"Testing",len(snr),"different SNR values through",repetitions,"repetitions."
    print"Expected individual test time of",timePerTest,'seconds.'
    print"Expected total test time of",totalTime/60.,"minutes. (",totalTime/3600.,"hours)\n\n"
    runTest = raw_input("Are you sure you want to run this test. (y/n): ")
    if runTest != "y":
        return

    startTime = time()

    curTest = 1
    for i in range(1,repetitions+1):
        testName = str(i)+".SNRTest"
        for j in snr:
            testTime = time()
            print"---------------------- Interation:",i," SNR Value:",j,'-----------------------'
            noise = 1 / np.power(10, j / 10.)  # convert from dB SNR to linear.
            print("Running GNU Radio")
            grc = All_One_Comp.All_One_Comp(noise)
            grc.start()
            grc.wait()

            print("Running Packetize")
            packetize.unpack("Output", "pkt", "Outputs", delete=1, debug=-1)

            print("Running BER Test")
            BER_test.test(testName,j,folder,debug=0)

            ## Generate status report
            print"------------------------------ Testing Status ------------------------------"
            print"Finished Test Number:",curTest,"of",numOfTests,'total.'
            print"Test time:",time()-testTime,'seconds'
            print"Elapsed Time:",(time()-startTime)/60.,'minutes (',(time()-startTime)/3600.,'hours)'
            remaining = (numOfTests-curTest)*((time()-startTime)/curTest) # number of test remaining times average time per test so far.
            print"Estimated Time Remaining:",remaining/60.,"minutes (",remaining/3600.,'hours)'
            print"----------------------------------------------------------------------------\n\n"
            curTest = curTest + 1


if __name__=='__main__':
    snrBest = 6
    snrWorse = -3
    dataPoints = 20
    repetitions = 5
    topFolder = 'simTests'

    folder = topFolder+'/'+datetime.now().strftime("%m-%d-%H:%M")
    os.makedirs(folder)
    snr = np.linspace(snrBest,snrWorse,dataPoints)
    main(snr,repetitions,folder)