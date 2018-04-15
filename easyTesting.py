from shutil import copyfile

action = raw_input("1:Host Test   2:Remote Test   ")

if action == "1":
    while 'q' not in action:
        action = raw_input("1:Reset Output, 2:Pic Response, 3:All Received  ")

        if action == "1":
            print("Resetting output file.")
            copyfile("OutEmpty","Output")
        elif action == "2":
            print("Changing to picture response.")
            copyfile("OutPic","Output")
        elif action == "3":
            print("Changing to all received.")
            copyfile("OutDone","Output")


if action == "2":
    while 'q' not in action:
        action = raw_input("1:Reset Output, 2:Pic Request, 3:Ack Response  ")

        if action == "1":
            print("Reseting output file.")
            copyfile("OutEmpty","Output")
        elif action == "2":
            print("Changing to picture request.")
            copyfile("OutPic","Output")
        elif action == "3":
            print("Chacking to Ack Response.")
            copyfile("OutAck","Output")
