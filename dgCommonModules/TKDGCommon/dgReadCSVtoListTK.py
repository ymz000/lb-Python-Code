#!/usr/bin/env python
"""
====================
dgReadCSVtoListTK.py
====================

Functions to read a CSV file into a list and return the list.

Intended to be imported into another Python program.

==========
Background
==========

==================
Installation/Usage
==================

- Put this file into the folder C:/Python27/Lib/site-packages/dgCommonModules

Typical use

- myCSVFileReadClass = ReadCSVtoList()	# instantiate the class
- myCSVFileReadClass.setVerboseMode(True)	# turn on verbose mode until all is working 
- csvAsReadIn = myCSVFileReadClass.findOpenReadCSV(defaultPath,'Select CSV File')	# read in CSV into list
- if csvAsReadIn == []:
-  return False

===
API
===

"""
from __future__ import print_function

from builtins import object
import os
import datetime
import time
import sys

#sys.path.append('C:\\Python37\\Lib\\site-packages\\dgCommonModules\\TKDGCommon')

try:
	from dgProgDefaultsTK import *
except:
	print('Need to load dgProgDefaultsTK into site-packages')
try:
	from dgCheckFileFreshTK import *
except:
	print('Need to load dgCheckFileFreshTK into site-packages')
	
from tkinter import filedialog
from tkinter import *
from tkinter import messagebox

lastPathFileName = ''

verboseMode = False
freshFlag = False
useSniffer = False

def errorDialog(errorString):
	messagebox.showerror("Error", errorString)

def infoBox(msgString):
	messagebox.showinfo("pyReadCSVtoListTK",msgString)

class ReadCSVtoList(object):
	def findOpenReadCSV(self, defaultPath='', dialogHeader='Open File'):
		"""
		:global lastPathFileName: The path asset by this function based on the path found by the browser.
		:global verboseMode: Set to true if you want diagnostic messages printed along the way. Verbose Mode can also be changed by calling setVerboseMode().

		:param defaultPath: Optional default path. If none is entered defaults to empty.
		:param dialogHeader: Optional headers that is printed on the top of the screen.
		:return: The contents of the file as a list. If cancel was pressed on the file selector or the file is empty, returns an empty list.
		
		This is the main method which calls the other methods in this class.		
		"""
		global lastPathFileName
		global verboseMode
		if verboseMode:
			print 'findOpenReadCSV: got here'
		inPathFilename = self.findInputCSVFile(defaultPath, dialogHeader)
		if inPathFilename == '':
			if verboseMode:
				errorDialog('Input file was not selected')
			return []
		inPathFilename = os.path.normpath(inPathFilename)
		lastPathFileName = inPathFilename
		defaultPath = inPathFilename[0:inPathFilename.rfind('\\')+1]
		if verboseMode:
			print("findOpenReadCSV: defaultPath",defaultPath)
		myDefaultHandler = HandleDefault()
		myDefaultHandler.storeKeyValuePair('DEFAULT_PATH',defaultPath)
		if verboseMode:
			print('Input file name :', end=' ')
			print(self.extractFilenameFromPathfilename(inPathFilename))
		if freshFlag:
			myFreshCheck = CheckFreshness()
			if not myFreshCheck.isFresh(inPathFilename):
				if verboseMode:
					print('fresh flag was set to check freshness for CSV files')
				errorDialog("The CSV File is not fresh\nEither change the Options to ignore the freshness check\nor create/choose a fresh file")
				return []
		csvFileAsReadIn = self.readInCSV(inPathFilename)
		if csvFileAsReadIn == []:
			errorDialog("Didn't read in any BOM contents")
		if verboseMode:
			print("findOpenReadCSV: BOM is",csvFileAsReadIn)
		return csvFileAsReadIn

	def findInputCSVFile(self,defaultPath,bomFileString='Select File to Open'):
		"""
		:param defaultPath: The path that was selected. The calling function is responsible for remembering the name.

		:returns: pathfilename of the file that was selected or empty string if no file was selected.
		
		Uses filechooser to browse for a CSV file.		
		"""
		inFileNameString =  os.path.normpath(filedialog.askopenfilename(initialdir = defaultPath,title = "Select file",filetypes = (("csv files","*.csv"),("all files","*.*"))))
		return inFileNameString
			
	def extractFilenameFromPathfilename(self, fullPathFilename):
		"""
		:param fullPathFilename: The path and file name
		
		:returns: Path without the filename at the end

		Extract fileName without extension from pathfullPathName
		"""
		return(os.path.normpath(fullPathFilename[fullPathFilename.rfind('\\')+1:]))

	def readInCSV(self, inFileN):
		"""
		:global useSniffer: Flag which indicates whether or not to use the file sniffer. Set the sniffer flag by setUseSnifferFlag().
		
		:param inFileN: Input pathfilename

		:returns: List which contains the contents of the CSV file
		
		Reads a CSV file into a list. This method 
		"""
		global useSniffer
		# select the input file names and open the files
		intFileHdl = open(inFileN, 'r')
		if useSniffer:
			print('using sniffer')
			try:
				dialect = csv.Sniffer().sniff(intFileHdl.read(2048))
			except:
				intFileHdl.seek(0)
				reader = csv.reader(intFileHdl, delimiter='\t')
				csvListIn = []
				for row in reader:
					csvListIn.append(row)
				return csvListIn
			intFileHdl.seek(0)
			reader = csv.reader(intFileHdl, dialect)
		else:
			reader = csv.reader(intFileHdl)
		
		# read in the CSV file into csvListIn
		csvListIn = []
		for row in reader:
			csvListIn.append(row)
		return csvListIn

	def getLastPathFileName(self):
		"""
		:global lastPathFileName: the last path file name that was used
		
		:returns: the last path file name
		
		getLastPathFileName - Used by external calling methods to determine what the path/filename 
		of the last file that was read in was.
		"""
		global lastPathFileName
		return os.path.normpath(lastPathFileName)

	def getLastPath(self):
		"""
		:global lastPathFileName: the last path file name that was used
		
		:returns: the last path file name
		
		getLastPathFileName - Used by external calling methods to determine what the path/filename 
		of the last file that was read in was.
		"""
		global lastPathFileName
		lastPathFileName = os.path.normpath(lastPathFileName)
		return(os.path.normpath(lastPathFileName[0:lastPathFileName.rfind('/')+1]))

	def getLastFileNameNoExt(self):
		"""
		:global lastPathFileName: the last path file name that was used
		
		:returns: the last path file name

		getLastFileNameNoExt - Used by external calling methods to determine what the filename 
		of the last file that was read in was.
		"""
		global lastPathFileName
		lastPathFileName = os.path.normpath(lastPathFileName)
		return lastPathFileName[lastPathFileName.rfind('/')+1:-4]

	def setVerboseMode(self,verboseFlag):
		"""
		:param verboseFlag: Value To set verbose Flag True False
		
		Sets the verbose flag.
		The verbose flag can be used to see into the actions 
		of this module without changing the module in debug.
		The verbose messages go to the command prompt window.
		"""
		global verboseMode
		verboseMode = verboseFlag
		return True
	
	def setFreshCheckFlag(self,freshnessFlag):
		"""
		:global freshFlag: Flag value stored as a global for use directly by other functions
		:global verboseMode: Verbose flag.
		
		:returns: True always
		
		Set the freshness check flag.
		This flag is used to determine whether or not to check the file freshness before opening it.
		If this flag is set the file has to be created on the same day that this method is invoked.
		This is intended to be set from other modules which use this class.		
		"""
		global freshFlag
		global verboseMode
		if verboseMode:
			print('CheckFreshness:setFreshCheckFlag: setting freshness flag', freshnessFlag)
		freshFlag = freshnessFlag
		return True
		
	def getFreshFlag(self):
		"""
		:global freshFlag: Flag value stored as a global for use directly by other functions
		:global verboseMode: Verbose flag.
		
		:returns: the value of the fresh check flag.

		Return the value of the freshness check flag
		"""
		global freshFlag
		global verboseMode
		if verboseMode:
			print('CheckFreshness:getFreshFlag: getting freshness flag',freshFlag)
		return freshFlag

	def setUseSnifferFlag(self,snifferFlag):
		"""
		:global useSniffer: Flag that determines whether or not to use the CSV sniffer.

		:returns: True always
				
		Set the flag for whether or not the CSV sniffer should be used when reading the CSV file.
		The sniffer can determine the input file style of the delimiter (comma separated, tab separated, etc.)
		
		"""
		global useSniffer
		useSniffer = snifferFlag
		return True
		