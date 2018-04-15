from shutil import copyfile

action = raw_input("1:Host Test   2:Remote Test   3:Test Both   ")

if action == "1":
    while 'e' not in action:
        action = raw_input("1:Reset Output   2:Pic Response   3:All Received  ")

        if action == "1":
            print("Resetting output file.")
            copyfile("OutEmpty","Output")
        elif action == "2":
            print("Changing to picture response.")
            copyfile("OutPic","Output")
        elif action == "3":
            print("Changing to all received.")
            copyfile("OutDone","Output")


elif action == "2":
    while 'e' not in action:
        action = raw_input("1:Reset Output   2:Pic Request   3:Ack Response  ")

        if action == "1":
            print("Reseting output file.")
            copyfile("OutEmpty","Output")
        elif action == "2":
            print("Changing to picture request.")
            copyfile("OutPic","Output")
        elif action == "3":
            print("Changing to Ack Response.")
            copyfile("OutAck","Output")

elif action == "3":
    while 'e' not in action:
        action = raw_input("1:Reset Output   2:Swap TX_Input with Output  ")

        if action == "1":
            print("Resetting output file.")
            copyfile("OutEmpty","Output")
        elif action == "2":
            print("Swapping TX_INPUT with Output.")
            copyfile("TX_INPUT.bin","Output")
else:
    print("Later loser.")
