import os

def watchFile(fileName,change="size",interval=50,changeHold = -1):
    # Watches for changes to the file fileName.
    # Change is the property that is being watched for changes.
    # Interval is the frequency that changes are checked.
    # ChangeHold indicates how many checks need to be without change so that the function indicates changes have stopped.
    # ChangeHold set to -1 will result in watchFile returning 1 as soon as a change is detected.
    # ChangeHold set to 3 will result in watchFile returnig 1 after three checks have been made where no change was detected AFTER an initial change was detected.

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

