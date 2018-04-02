import masters
from datetime import datetime
import numpy as np
import threading, time
from time import sleep

def main(system,startTime,power, repetitions, testFrequency, folder):

    # Initilize some stuff
    test = testHandler(power, repetitions, testFrequency, folder)

    # Make sure that we will be able to call the GNU Radio Files.
    masters.testGRCs()

    if system == "host":
        timeDelta = (startTime - datetime.now()).total_seconds()
        threading.Timer(timeDelta,test.host).start()
    elif system == "remote":
        timeDelta = (startTime - datetime.now()).total_seconds()
        threading.Timer(timeDelta, test.remote).start()

class testHandler():
    def __init__(self,power, repetitions, testFrequency, folder):
        self.power = power
        self.repetitions = repetitions
        self.testFrequency = testFrequency
        self.folder = folder
        self.sequential = 1 # 1 = non sequential, 0 = sequential

    def host(self):
        print("Starting test of host system.")

        startTime = time()

        hostThread = threading.Thread(target=self.runhost)

        curTest = 1
        for i in range(1,self.repetitions+1):
            testName = str(i)+".PowerTest"
            for j in self.power:
                testTime = time()
                print"---------------------- Interation:", i, " IF Power Level:", j, '-----------------------'
                self.curpower = j
                hostThread.start() # Start the test in a thread
                sleep(testFrequency) # Test frequency should already be in seconds.
                hostThread.stop() # Stop the test after the appropriate amount of time has passed.



    def runhost(self):
        masters.host(self.sequential,self.curpower,userinput=0)


    def remote(self):
        print("Starting test of remote system.")

    def runremote(self):


if __name__=='__main__':
    print("Starting LISSA Automated Hardware Test Software")
    print("Please specify the following test conditions:")
    print("!!!Understand that these settings should be matched to the other system!!!")


    userInput = 1
    if userInput == 1:
        correct = 0
        while correct == 0:
            system = raw_input("Is this the [H]ost or [R]emote system? ")
            if type(system) == str:
                if ('H' in system) or ('h' in system):
                    system = 'host'
                    correct = 1
                elif ('R' in system) or ('r' in system):
                    system = 'remote'
                    correct = 1
                else:
                    print("System must be specified as host or remote.")
            else:
                print("System must be specified as host or remote.")

        correct = 0
        while correct == 0:
            pmin = raw_input("Minimum IF gain of the SDR: ")
            if (type(pmin) == int) and (pmin >= 0 and pmin <= 50):
                correct = 1
            else:
                print("IF gain must be specified as an integer between 0 and 50.")
        correct = 0
        while correct == 0:
            pmax = raw_input("Maximum IF gain of the SDR: ")
            if (type(pmax) == int) and (pmax >= 0 and pmax <= 50):
                correct = 1
            else:
                print("IF gain must be specified as an integer between 0 and 50.")
        correct = 0
        while correct == 0:
            ppoints = raw_input("Number of power values to test at: ")
            if (type(ppoints) == int) and (ppoints > 0):
                correct = 1
            else:
                print("Number of points must be specified as a positive, nonzero number.")
    
            powerLevels = np.linspace(pmax,pmin,ppoints)
            power = powerLevels.round()
            power = list(set(power)) # Remove duplicates.
    
            if len(powerLevels) != len(power):
                print("After rounding, duplicate powers were detected and removed.")
                print("Current number of power levels to test is: " +str(len(power)))
                correct = raw_input("Is this change acceptable? [1/0]")
    
        correct = 0
        while correct == 0:
            repetitions = raw_input("Number of test repetitions.")
            if repetitions > 0 and type(repetitions) == int:
                correct = 1
            else:
                print("The number of repeitions must be a positive integer.")
    
        correct = 0
        while correct == 0:
            print("How many minutes should be allowed for each test to complete?")
            testFrequency = raw_input("Warning: Tests will be stopped if not given enough time. ")
            if type(testFrequency)==int and testFrequency > 0:
                correct == 1
                testFrequency = testFrequency * 60
            else:
                print("The number of minutes between tests must be specified as a positive integer.")
    else:
        # Set user input to 0 and then adjust these settings for faster test starting.
        system = 'host'
        pmin = 10
        pmax = 40
        ppoints = 5
        power = np.linspace(pmax,pmin,ppoints)
        repetitions = 3
        testFrequency = 3 # Minutes
        testFrequency = testFrequency * 60 # convert to seconds.

    numOfTests = len(power) * repetitions
    totalTime = numOfTests * testFrequency

    print"\n\nPreparing Automated Tests for the",system,"system."
    print"Testing", len(power), "different power levels over", repetitions, "repetitions."
    print("        Power levels ranging from "+str(pmin)+" to "+str(pmax)+" dB gain IF.")
    print"Each test is given ", testFrequency, 'seconds to attempt to complete.'
    print"Total test time will take ", totalTime / 60., "minutes. (", totalTime / 3600., "hours)\n\n"

    runTest = raw_input("Are you sure you want to run this test. (y/n): ")

    correct = 0
    while correct == 0:
        startTime = raw_input("What time should these test start? (Must match with other system!). [HH:MM]")
        try:
            timeObject = datetime.strptime(startTime,"%H:%M").time()
            day = datetime.now().date()
            specificStart = datetime.combine(day,timeObject)
        except ValueError:
            print("Time must be specified in 24hr format in format 'HH:MM'.")

    main(system,specificStart,power,repetitions=repetitions,testFrequency=testFrequency)