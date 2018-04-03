########Must first do "sudo apt-get install fswebcam"
########Then must do "sudo apt-get install python-imaging-tk"
import os
import time
from Tkinter import *
import Image, ImageTk
from functools import partial

#Camera class for attaining parameters and taking the picture!
class Camera:
	#Get the parameters necessary for the camera to take the picture such as cropping and brightness.
	def getParameters(self):
		global SelectCamera, Grayscalevalue, Scaleto, saturation, gain, sharpness, hue, brightness, contrast, \
		title, framesps, StatusLines, Resolution, frames, File, start_width, start_height, cropped_width, cropped_height
		Updates = "None" #Enter Many, Some, or None as a string       
		if Updates == "Many":
			StatusLines = "-v"
		elif Updates == "Some":
			StatusLines = ""
		else:
			StatusLines = "-q"

		#Choosing the Camera
		CameraSelection = "Webcam" #Set this to Webcam as a string for an external camera unless you want the embedded camera on the computer.
		if CameraSelection == "Webcam":
			SelectCamera = "-d /dev/video1 "
		else:
			SelectCamera = "-d /dev/video0 "

		#Saving the file
		#Save a file with the date and time to the desktop?
		DateandTime = "No" #Enter Yes as a string if so.
		Filename = "SDRSatcom" #Enter the filename as a string
		current = "$(date +\%Y\%m\%d\%H\%M\%S)"
		if DateandTime == "Yes":
			File = " ~/Desktop/" + Filename + current +  ".jpeg"
		else:
			File = " ~/Desktop/" + Filename + ".jpeg"

		#Insert a title for the picture
		title = "SDRSatcom"

		#Resolution options: 640x480, 352x288, 160x120
		High = "640x480"
		Medium = "352x288"
		Low = "160x120"
		Resolution = High #Change this to be High, Medium, or Low

		#Scale image
		Scaleto = High #Change this to either High, Medium, or Low

		#Enter the number of frames
		frames = 3

		#Greyscale?
		Greyscale = "No" #Enter Yes as a string for greyscale, anything else for no greyscale
		if (Greyscale == "Yes"):
			Grayscalevalue = "--greyscale"
		else:
			Grayscalevalue = ""

		#Cropping
		#Starting cropping position
		start_width = 0 #upper left
		start_height = 0 #upper left
		cropped_width = 400
		cropped_height = 400


		#Enter a percentage for each parameter
		brightness = 50 
		sharpness = 50
		gain = 50
		contrast = 60
		hue = 50
		saturation = 75

		#Unable to change the number of fps, usually its about 17 fps
		#If we could change the fps, this is where we would do it.
		framesps = 20
	#Called to take a picture with the camera. Returns the picture surface.
 	def takePicture(self):
		systemcall = "fswebcam " + SelectCamera +\
		Grayscalevalue + " --scale " + \
		Scaleto + "-s saturation=" + \
		str(saturation) + "% -s hue=" + str(hue) + \
		"% -s contrast=" + str(contrast) + \
		"% --bottom-banner --title " + str(title) \
		+ " --fps " + str(framesps) + " -s gain=" \
		 + str(gain) + "% " + StatusLines + " -s sharpness=" + \
		 str(sharpness) \
		+ "% -s brightness=" + str(brightness) +\
		 "% -p YUYV -r " + Resolution +  " --jpeg -1 -F " \
		 + str(frames) + File
		os.system(systemcall)
		#print "Took a picture."

#Cropping Class
class Crop:
	def Open(self):
		global picture_to_open
		picture_to_open = Image.open("SDRSatcom.jpeg")
		#picture_to_open.show() #Uncomment to display original picture.
		newimage = picture_to_open.crop((start_width,start_height,cropped_width,cropped_height))
		newimage.save("newimage.jpeg")
		new_picture_to_open = Image.open("newimage.jpeg")
		#new_picture_to_open.show()	#Uncomment to display cropped picture.
		#print("Hello. Opened picture.")

#Class for resizing the canvas to be full screen!
class ResizingCanvas(Canvas):
    def __init__(self, parent, **kwargs):
        Canvas.__init__(self, parent, **kwargs)
        self.bind("<Configure>", self.on_resize)
        # Set the width and the height of the canvas to the size of the window minus the padding
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self, event):  # This is what will handle the window being resized.
        # Determine the ratio of old width/height to new width/height
        wscale = float(event.width) / self.width
        hscale = float(event.height) / self.height
        self.width = event.width
        self.height = event.height
        # Resize the canvas
        self.config(width=self.width, height=self.height)
        # Rescale all objects tagged with the "all" tag
        self.scale("all", 0, 0, wscale, hscale)

#Defines the exit functionality!
def gracefull_exit():
    print("User quit the program.")
    exit(0)



############################################################################################################
#SCREENS

####################################################
#Functions

#Switches screens
def switchscreen(start, end):
	global current_screen
	start.place_forget()
	end.place(x=0,y=0,relheight=1,relwidth=1)
	current_screen = end

#####################################################
#Classes for Screens
class rootClass:
	def rootdefinition(self):
		print "Started Root Class"
		#Sets root to be a global variable so that other classes can use it for their frames.
		global root, WelcomeScreen
		#Creates the window
		root = Tk()

	    # Creates the menu
		menu = Menu(root)
		root.config(menu=menu)

		#Innitialize Frames so that I can refrence them before they are explicitly defined.
		WelcomeScreen = Frame(root, width= 100, height = 100)
		CaptureImageScreen = Frame(root, width= 100, height = 100)

	    # Creates the file dropdown
		file=Menu(menu)
		file.add_command(label="Exit",command=gracefull_exit)
		file.add_command(label="Select Camera",command=gracefull_exit)#Camera.select_cam)
		menu.add_cascade(label="File",menu=file)

		#Aquires the size of the screen, gives the title and root background colour.
		w, h = root.winfo_screenwidth(), root.winfo_screenheight()
		root.geometry("%dx%d+0+0" % (w, h))
		root.configure(background='#6C93BF')
		root.title("SDRSatcom - Root")

		#Start Button
		Start_Button = Button(root, text = "Start!")
		Start_Button.configure(width = 400, height = 100, bg="green", fg="black", command = switchscreen(menu, WelcomeScreen))
		Start_Button.pack(side = TOP, fill = BOTH, expand = True)

		#Where the program begins
		root.mainloop() #####################################################################################################It really matters where this is placed.

		print "Finished Root Class"
#WelcomeScreen
class WelcomScreenCreation:	
	def WelcomeScreenCreationFuntion(self):
		global WelcomeScreen
		#Creates the frame
		#WelcomeScreen = Frame(root, width= 100, height = 100)
		WelcomeScreen.configure(background='#6C93BE') #It says that WelcomeScreen has been destroyed...
		WelcomeScreen.place(x=0, y=0, relheight=1, relwidth=1)
		root.title("SDRSatcom - Welcome Screen")
		WelcomeScreen.pack(fill=BOTH,expand=True)

		#Get the SDR image
		SDR_image = PhotoImage(file = 'SDRpicture.png')
		SDR_label = Label(WelcomeScreen, image = SDR_image)
		SDR_label.configure(width = 800, height = 300, bg="green", fg="black")
		SDR_label.pack(side=TOP, fill = BOTH, expand = True)

		#Create button to move to next screen once camera is connected.
		Button_CameraConnected = Button(WelcomeScreen,text = "Plug in your Webcam, then click here to begin...")
		Button_CameraConnected.configure(width = 1600, height = 900,bg="green", fg="black", command = gracefull_exit)
		Button_CameraConnected.pack(fill=X, expand = True, side = BOTTOM)
		print "Finished Welcome Screen Function"
#Capture Image Screen
class CaptureImageScreenCreation:
	def CaptureImageScreenCreation(self):
		#Creates the frame
		#CaptureImageScreen = Frame(root, width= 100, height = 100)
		CaptureImageScreen.pack(fill=BOTH,expand=True)
		CaptureImageScreen.configure(background='#6C93BF')
		root.title("SDRSatcom - CaptureImageScreen")

		#Create the frames we are using
		#Center frame holds the main content, pictures ect.
		CaptureImageScreen_centerframe = Frame(CaptureImageScreen)
		CaptureImageScreen_centerframe.pack(fill=BOTH, expand=True)
		Button_CaptureImage = Button(CaptureImageScreen_centerframe,text = "Click Here to Capture Image!")
		Button_CaptureImage.configure(width = 400, height = 100,bg="green", fg="black", command = gracefull_exit)
		Button_CaptureImage.pack(fill=X, expand = True, side = BOTTOM)
		#Top frame shows the progress through the setup.
		CaptureImageScreen_topframe = Frame(CaptureImageScreen)
		CaptureImageScreen_topframe.pack(fill=BOTH, expand=True, side=TOP)

		#Bottom frame
		CaptureImageScreen_bottomframe = Frame(CaptureImageScreen)
		CaptureImageScreen_bottomframe.pack(fill=BOTH,expand=True, side=BOTTOM)
		print "Finished Capture Image Screen Function"

#################################################################################################################

#Main function
def main():
	#Calling the root to create the window
	rootClasscall = rootClass()
	rootClasscall.rootdefinition()
	#Calling the Welcome Screen to start
	WelcomeScreenCreationVariable = WelcomScreenCreation()
	WelcomeScreenCreationVariable.WelcomeScreenCreationFuntion()
	
# intro_frame = Frame(root, width=w, height=h)
# start_screen.place(x=0, y=0, relheight=1, relwidth=1)

# next_button_img = PhotoImage(file = 'files/forward_button.png')
# next = Button(option_frame, image = next_button_img, command=do3)
# do2 = partial(switchscreen, option_frame, start_screen)

# systems_log = Button(menu_frame, image = b5, bd=0, command = slog, activebackground='#6C93BE')#text='STOP', command=S)
# systems_log.configure(background='#6C93BE',highlightbackground='#6C93BE')
# systems_log.place(relx = 0.6 ,rely = 0.38, anchor='center') #ask what stop button should do

	#Tests
	# Test_Root_screen = Frame(root,width = h, height = h)
	# Test_Root_screen.configure(background='#6C93BE')
	# Test_Root_screen.pack(expand = True)
	# Frame_test = Frame(Test_Root_screen)
	# Test_Root_screen.configure(background='#6C93BF')
	# Frame_test.pack(side=TOP, expand = True)
	# bottom_frame_test = Frame(Frame_test)
	# bottom_frame_test.pack(side=BOTTOM)
	# Button_test = Button(Frame_test,text = "Test Button", command = gracefull_exit)
	# Button_test.pack(side = LEFT,padx = 100)
	# Button_test2 = Button(Frame_test,text = "Test Button 2", command = gracefull_exit)
	# Button_test2.pack(side = LEFT)
	# Button_test3 = Button(bottom_frame_test,text = "Test Button 3", command = gracefull_exit)
	# Button_test3.pack(side = BOTTOM)
	# Frame_test_Under = Frame(Test_Root_screen)
	# Frame_test_Under.pack(fill=BOTH,side=TOP,expand = True)
	# Button_test_under = Button(Frame_test_Under,text = "Test Button Under", command = gracefull_exit)
	# Button_test_under.pack(side = LEFT,padx = 100)

    # Create the frames we are using
    # Center frame holds the main content, pictures ect.
	# WelcomeScreen_centerframe = Frame(WelcomeScreen)
	# WelcomeScreen_centerframe.pack(fill=X, expand=True)

    # Top frame shows the progress through the setup.
	# WelcomeScreen_topframe = Frame(WelcomeScreen)
	# WelcomeScreen_topframe.pack(fill=X, expand=True, side=TOP)

    # Bottom frame
	# WelcomeScreen_bottomframe = Frame(WelcomeScreen)
	# WelcomeScreen_bottomframe.pack(fill=X,expand=True, side=BOTTOM)
	# print "Made it past frame declaration"
	# Button_test = Button(WelcomeScreen,text = "Test Button", command = gracefull_exit)
	# Button_test.pack(fill=X,side=BOTTOM)
	# #Test labels.
	# w = Label(WelcomeScreen_topframe, text="WelcomeScreen_topFrame, red", bg="red", fg="white")
	# w.pack(fill=BOTH, expand = True) #Use "ipadx=100,ipady = 100" in order to specify the dimensions.
	# w = Label(WelcomeScreen_centerframe, text="WelcomeScreen_centerFrame, green", bg="green", fg="black")
	# w.pack(fill=BOTH, expand = True)
	# w = Label(WelcomeScreen_bottomframe, text="WelcomeScreen_bottomFrame, blue", bg="blue", fg="white")
	# w.pack(fill=BOTH, expand = True)
	# print "Made it past frame Labels"
	#CaptureImageScreen

    # Show progress through setup procedure
	#progressLabel1 = Label(topFrame, text="Select Camera")
	#progressLabel1.pack(side=LEFT)
	#progressLabel2 = Label(topFrame, text="Capture Image")
	#progressLabel2.pack()
	#progressLabel3 = Label(topFrame, text="Crop Image")
	#progressLabel3.pack(side=RIGHT)

    # Create buttons to move through the process

	#mycanvas = ResizingCanvas(centerFrame, width=1200, height=1000, highlightthickness=0)

	#Call classes to take the picture.
	
	'''
	Cameraclass = Camera()
	Cameraclass.getParameters()
	Cameraclass.takePicture()
	time.sleep(3) #This waits 3 seconds for the file to appear in the folder.

	#Call class to crop the image
	Cropclass = Crop()
	Cropclass.Open()
	image_width = picture_to_open.size[0]
	#print "image width = ",image_width
	image_height = picture_to_open.size[1]
	#print "image height = ",image_height
	'''



    # Load the image
	#rawImage = Image.open("SDRSatcom.jpeg")
	#rawImage = ImageTk.PhotoImage(rawImage)
	#imagesprite = mycanvas.create_image(300, 300, image=rawImage)
    # add some widgets to the canvas

	#mycanvas.pack(fill=BOTH, expand=YES)
    # tag all of the drawn widgets
	#mycanvas.addtag_all("all")
	print "Done"
	print "Press control Z to quit."

#Starts the main function
if __name__ == "__main__":
    main()







