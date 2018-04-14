#Created for GMU Senior Design Project L-Band SDR SATCOM
#Last Edited by William on 10/30/2017

#This module contains functions to split and recombine files using unix commands

#This file was written to run on a unix system.
#Tested with Ubuntu 17.10 with Python 2.7.14

def cut(original,prefix,fSize,debug=0):
	#Import usefull functions
	from subprocess import call as sysCall
	from os import stat as fileStat
	from pathlib2 import Path as path 
	
	#Check for input errors
	if type(original) != str:
		raise TypeError('filename should be specified in a string.')
	if not path(original).is_file():
		raise IOError('File does not exist.')

	if type(prefix) != str:
		prefix == str(prefix)

	#Determine the original size of the file
	originalSize = fileStat(original).st_size
	
	if type(fSize) != int:
		raise TypeError("Segmented size should be an integer of bytes.")
	if fSize > originalSize/2.:
		raise ValueError('Segmented size larger than half original file size.')

	#Determine the number of files that will be created
	filesCreated = str(int((float(originalSize)/float(fSize))+0.5))

	if len(filesCreated) > 4:
		raise ValueError('Function does not support more than 9,999 split files.')
	

	bytes = ["-b",str(fSize)]
	suffix = ["-d","-a","4"]
	command = ["split"]+suffix+bytes+[original,prefix]
	sysCall(command)

def comb(prefix,fileName,rmv=0):
	#Import usefull functions
	from subprocess import call as sysCall
	from os import remove as sysRemove
	from os import listdir as listdir
	from pathlib2 import Path as path

	#Check for input errors
	if type(prefix) != str:
		raise TypeError('prefix should be specified in a string.')

	if type(fileName) != str:
		raise TypeError('Filename must be specified in a string.')
	if path(fileName).is_file():
		print('!Warning!: The export filename specified already exists!')
		response =input('Continue? [y/n]')
		if response != 'y':
			raise ValueError('Specified filename aready exists, user quit.')
	
	#Combine the split files into one file.
	command = "cat "+prefix+"*"+" > "+fileName
	sysCall(command,shell=True)
