# pyDirCSV.py - Read a directory structure into a CSV file
# This can be used for things like comparing two directory trees in EXCEL
# Code is written to work with Windoze dir command line output

import pygtk
pygtk.require('2.0')

import gtk

# Check for new pygtk: this is new class in PyGtk 2.4
if gtk.pygtk_version < (2,3,90):
   print "PyGtk 2.3.90 or later required"
   raise SystemExit

import csv
import os
import sys

# this class does all the work of reading a directory tree into a list of lists
# each line in the list has
# 0 - Date
# 1 - Time
# 2 - Size
# 3 = FileName
# 4 - Path
class readDirectoryToList:
	# browseToFolder - Opens a windows file browser to allow user to navigate to the directory to read
	# returns the file name of the path that was selected
	def browseToFolder(self):
		dialog = gtk.FileChooserDialog(title="Select folder", 
			buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK)) 
		filter = gtk.FileFilter() 
		filter.set_name("Select Folder")
		filter.add_pattern("*") # what's the pattern for a folder 
		dialog.add_filter(filter)
		dialog.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			retFileName = dialog.get_filename()
			dialog.destroy()
			return(retFileName)
		elif response == gtk.RESPONSE_CANCEL: 
			print 'Closed, no files selected'
			dialog.destroy()
			exit()
	
	# Support for drag and drop or command line execution
	# returns the path to the directory
	# if the path can't be determined returns an empty string
	def dealWithCommandLine(self):
		pathToDir = ""
		if sys.argv[0][-11:] == 'pyDirCSV.py':		# running from the command line
			if len(sys.argv) == 2:
				pathToDir = sys.argv[1]
			elif len(sys.argv) == 1:
				None
		elif len(sys.argv) > 2:						# command line with too many passed values
			print 'usage pyDirCSV path_to_search'
			s = raw_input('--> ')
			exit()
		elif len(sys.argv) == 2:					# run from drag/drop
			pathToDir = sys.argv[0] 
		return(pathToDir)
		
	# formCommandLine - Forms the command line string
	# returns the command line string
	def formCommandLine(self, makeDirPath):
		makeDirPath = '\"' + makeDirPath + '\"'		# path might have spaces, etc
		commandLine = 'dir '
		commandLine += makeDirPath
		commandLine += ' /-c /s > c:\\temp\\tempDir.txt'
		return(commandLine)
			
	# parse through the text file that was created when the directory was set up
	# returns a list of lists
	def parseDirTxt(self, filePtr):
		dirFiles = []
		dirName = ""
		for textLine in filePtr:
			textLine = textLine.strip('\r\n')
			if len(textLine) == 0:
				None
			elif textLine.find("Volume in drive ") != -1:
				None
			elif textLine.find("Volume Serial Number is") != -1:
				None
			elif textLine.find("Directory of ") != -1:
				dirName = textLine[14:].strip()
			elif textLine.find('<DIR>') > 0:
				None
			elif textLine.find('/') == 2:
				dirLine = []
				dirLine.append(textLine[0:10])
				dirLine.append(textLine[12:20])
				dirLine.append(textLine[22:38].strip())
				dirLine.append(textLine[39:])
				dirLine.append(dirName)
				dirFiles.append(dirLine)
			elif textLine.find('File(s)') > 0:
				None
			elif textLine.find('     Total Files Listed:') > 0:
				None
			elif textLine.find(' Dir(s)') > 0:
				None
		return(dirFiles)
		
	# deleteTempFile - delete the temporary file that was created
	def deleteTempFile(self):
		try:
			os.system('del c:\\temp\\tempDir.txt')
		except:
			print "Couldn't delete temp file"
			s = raw_input('Hit ENTER to continue --> ')
			exit()
	
	# doReadDir - 
	def doReadDir(self):
		pathToDir = readDirectoryToList.dealWithCommandLine(self)
		if pathToDir == '':
			pathToDir = readDirectoryToList.browseToFolder(self)
		commandString = readDirectoryToList.formCommandLine(self, pathToDir)
		rval = os.system(commandString)
		if rval == 1:		# error because the c:\temp folder does not exist
			print 'Creating c:\\temp folder'
			rval2 = os.system('md c:\\temp\\')
			if rval2 == 1:
				print 'unable to create c:\\temp\\ folder'
				s = raw_input('Hit ENTER to continue --> ')
				exit()
			rval = os.system(commandString)
		readFile = open('c:\\temp\\tempDir.txt','rb')
		dirFileL = readDirectoryToList.parseDirTxt(self, readFile)
		readFile.close()
		readDirectoryToList.deleteTempFile(self)
		return(dirFileL)
		
# this class allows the user to select the output file name and opens the output file as a csv file
class selOutputFile:
	# selectOutputFileName
	# returns the name of the output csv file
	def selectOutputFileName(self):
		dialog = gtk.FileChooserDialog(title="Save as", 
			buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK)) 
		filter = gtk.FileFilter() 
		filter.set_name("*.csv")
		filter.add_pattern("*.csv") # whats the pattern for a folder 
		dialog.add_filter(filter)
		dialog.set_action(gtk.FILE_CHOOSER_ACTION_SAVE)
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			retFileName = dialog.get_filename()
			dialog.destroy()
			return(retFileName)
		elif response == gtk.RESPONSE_CANCEL: 
			print 'Closed, no files selected'
		dialog.destroy()
		exit()
	
	# openCSVFile - opens the CSV output file as a CSV writer output
	def openCSVFile(self, csvName):
		if csvName[-4:] != '.csv' and csvName[-4:] != '.CSV':
			csvName += '.csv'
		try:
			myCSVFile = open(csvName, 'wb')
		except:
			print "Couldn't open the output file. Is the file open in EXCEL?"
			s = raw_input('Hit ENTER to exit --> ')	# wait for enter to be pressed
			exit()
		outFil = csv.writer(myCSVFile)
		return(outFil)
		
myReadFolder = readDirectoryToList()						# create readDirectoryToList instance
dirFileList = myReadFolder.doReadDir()						# read dir structure into a list

myOutFile = selOutputFile()									# create output file class
outCSVFileName = myOutFile.selectOutputFileName()			# get output file name
outFile = myOutFile.openCSVFile(outCSVFileName)				# Open the output csv file

# write out the file header followed by the file data
outFile.writerow(['Date','Time','Size','FileName','Path'])	# File header
outFile.writerows(dirFileList)

print 'Files : ', len(dirFileList)