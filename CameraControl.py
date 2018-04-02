########Must first do "sudo apt-get install fswebcam"
import os
import time
import PIL
from PIL import Image

#Camera class for taking the picture
class Camera:
    def takePicture(self):
        """Called to take a picture with the camera. Returns the picture surface."""
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
        print "Took a picture."

#Cropping Class
class Crop:
	def Open(self):
		global picture_to_open
		picture_to_open = Image.open("SDRSatcom.jpeg")
		picture_to_open.show()
		newimage = picture_to_open.crop((start_width,start_height,cropped_width,cropped_height))
		newimage.save("newimage.jpeg")
		new_picture_to_open = Image.open("newimage.jpeg")
		new_picture_to_open.show()	
		print("Hello. Opened passage.")

#Do you want status updates while code is running?
Updates = "Some" #Enter Many, Some, or None as a string       
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

#Main function
def main():
	Cameraclass = Camera()
	Cameraclass.takePicture()
	time.sleep(3) #This waits 3 seconds for the file to appear in the folder.
	print "Done!"

	#Cropping
	Cropclass = Crop()
	Cropclass.Open()
	image_width = picture_to_open.size[0]
	print "image width = ",image_width
	image_height = picture_to_open.size[1]
	print "image height = ",image_height

if __name__ == "__main__":
    main()







