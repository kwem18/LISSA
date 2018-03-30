import os
from time import sleep

def watchFile(fileName,change="size",interval=50,changeHold = 0):
    # Watches for changes to the file fileName.
    # Change is the property that is being watched for changes.
    # Interval is the frequency that changes are checked.
    # ChangeHold indicates how many checks need to be without change so that the function indicates changes have stopped.
    # ChangeHold set to 0 will result in watchFile returning 1 as soon as a change is detected.
    # ChangeHold set to 3 will result in watchFile returnig 1 after three checks have been made where no change was detected AFTER an initial change was detected.

    # Change unit of interval from milliseconds to seconds for sleep
    interval = interval/1000.

    supportChanges = ["size","modTime","accessTime"]

    if not change in supportChanges:
        raise ValueError("Supported Changes that can be watched are size, modTime, accessTime.")

    if type(interval) != int:
        raise TypeError("Polling interval must be specified as an integer. The unit is milliseconds.")
    if interval <= 0:
        raise ValueError("Polling interval must be a positive non-zero integer. The unit is milliseconds.")

    if type(changeHold) != int:
        raise TypeError("change hold must be specified as an integer.")

    if not os.path.isfile(fileName):
        raise IOError("fileName fails to point to a file that exists.")

    # Get the initial value
    lastValue = dynamicStat(fileName,change)

    # Stay in this loop until a change is detected.
    newValue = lastValue
    while newValue == lastValue:
        newValue = dynamicStat(fileName,change)
        sleep(interval)

    lastValue = newValue
    steadyReps = 0 # keeps track of number of occurences where no change to the file occured in the polling period.
    # Once a change is detected, enter this loop until changes aren't detected for changeHold repetitions
    while steadyReps != changeHold:
        newValue = dynamicStat(fileName,change)
        if newValue == lastValue:
            steadyReps += 1 # if no change was detected between polling intervals, increment the steady repetition counter.
        else:
            steadyReps = 0 # if a change was detected, reset the steady repetition counter.
        sleep(interval)
        lastValue = newValue # Set the newValue to the last value and loop again.

    success = 1

    return success



def dynamicStat(fileName,change):
    # Function called by watchFile
    # Input error checks done outside of function.
    if change == "size":
        result = os.stat(fileName).st_size
    elif change == "modTime":
        result = os.stat(fileName).st_mtime
    elif change == "accessTime":
        result = os.stat(fileName).st_atime
    return result