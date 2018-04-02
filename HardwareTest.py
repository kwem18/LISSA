import sys
sys.path.insert(0,'grc_files')
import All_One_Comp
import packetize
import BER_test
import numpy as np
from time import time
from datetime import datetime
import os


def main(powers,repetitions,folder):
    esttimePerTest = 35 # Seconds
    numOfTests = len(powers) * repetitions
    totalTime = esttimePerTest * numOfTests
    print"\n\nStarting Automated Tests."
    print"Testing",len(powers),"different Power levels through",repetitions,"repetitions."
    print"Expected individual test time of",esttimePerTest,'seconds.'
    print"Expected total test time of",totalTime/60.,"minutes. (",totalTime/3600.,"hours)\n\n"
    runTest = raw_input("Are you sure you want to run this test. (y/n): ")
    if runTest != "y":
        return

    startTime = time()

    curTest = 1
    for i in range(1,repetitions+1):
        testName = str(i)+".PowerTest"
        for j in powers:
            testTime = time()
            print"---------------------- Interation:",i," Poewr Level:",j,'-----------------------'
            print("Running GNU Radio")
            grc = All_One_Comp.All_One_Comp(j)
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
    highPower = 3
    lowPower = 0
    powerLevels = 4
    repetitions = 1
    topFolder = 'hardTests'

    folder = topFolder+'/'+datetime.now().strftime("%m-%d-%H:%M")
    os.makedirs(folder)
    powers = np.linspace(highPower,lowPower,dataPoints)
    main(powers,repetitions,folder)