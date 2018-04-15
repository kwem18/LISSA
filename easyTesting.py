from shutil import copyfile

while True:
    action = raw_input("1:Reset Output, 2:Pic Request, 3:Ack Response   ")

    if action == "1":
        print("Reseting output file.")
        copyfile("OutEmpty","Output")
    elif action == "2":
        print("Changing to picture request.")
        copyfile("OutPic","Output")
    elif action == "3":
        print("Chacking to Ack Response.")
        copyfile("OutAck","Output")
    else:
        print("Common man...")
