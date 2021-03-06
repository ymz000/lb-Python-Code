# Pt2-AoCDay23.py
# 2019 Advent of Code
# Day 23
# Part 2
# https://adventofcode.com/2019/day/23

from __future__ import print_function

import os
import sys
import time

"""
	--- Part Two ---
	Packets sent to address 255 are handled by a device called a NAT (Not Always Transmitting). The NAT is responsible for managing power consumption of the network by blocking certain packets and watching for idle periods in the computers.

	If a packet would be sent to address 255, the NAT receives it instead. The NAT remembers only the last packet it receives; that is, the data in each packet it receives overwrites the NAT's packet memory with the new packet's X and Y values.

	The NAT also monitors all computers on the network. If all computers have empty incoming packet queues and are continuously trying to receive packets without sending packets, the network is considered idle.

	Once the network is idle, the NAT sends only the last packet it received to address 0; this will cause the computers on the network to resume activity. In this way, the NAT can throttle power consumption of the network when the ship needs power in other areas.

	Monitor packets released to the computer at address 0 by the NAT. What is the first Y value delivered by the NAT to the computer at address 0 twice in a row?
	
	22391331247377 is too high.
	
"""

class CPU:
	""" CPU class
	Runs the program on the CPU 
	Takes input value
	Returns the output value
	"""
	
	def __init__(self):
		debug_initCPU = False
		self.programMemory = []
		self.setProgState('initCPU')
		self.programCounter = 0
		self.relativeBaseRegister = 0
		self.inputQueue = []
		self.outputQueue = []
		self.loadIntCodeProgram()
		if debug_initCPU:
			print("Memory Dump :",self.programMemory)
		
	def getOutputQueueLength(self):
		return len(self.outputQueue)
	
	def getInputQueueLength(self):
		return len(self.inputQueue)
	
	def loadIntCodeProgram(self):
		""" 
		"""
		debug_loadIntCodeProgram = False
		progName = "AOC2019D23input.txt"
		if debug_loadIntCodeProgram:
			print("Input File Name :",progName)
		with open(progName, 'r') as filehandle:  
			inLine = filehandle.readline()
			self.programMemory = map(int, inLine.split(','))
		for i in range(500):
			self.programMemory.append(0)
		if debug_loadIntCodeProgram:
			print(self.programMemory)

	def getProgState(self):
		""" Returns the value of the program state variable
		"""
		return self.progState
	
	def setProgState(self,state):
		""" Sets the value of the program state variable
		"""
		debug_setProgState = False
		self.progState = state
		if debug_setProgState:
			print("setProgState: self.progState =",self.progState)
			
	def intTo5DigitString(self, instruction):
		"""Takes a variable length string and packs the front with zeros 
		to make it 5 digits long.
		"""
		instrString=str(instruction)
		if len(instrString) == 1:
			return("0000" + str(instruction))
		elif len(instrString) == 2:
			return("000" + str(instruction))
		elif len(instrString) == 3:
			return("00" + str(instruction))
		elif len(instrString) == 4:
			return("0" + str(instruction))
		elif len(instrString) == 5:
			return(str(instruction))

	def extractFieldsFromInstruction(self, instruction):
		""" Take the Instruction and turn into opcode fields
		ABCD
		A = mode of 3rd parm
		B = mode of 2nd parm
		C = mode of 1st parm
		D = opcode
		
		:returns: [opcode,parm1,parm2,parm3]
		"""
		instructionAsFiveDigits = self.intTo5DigitString(instruction)
		parm3=int(instructionAsFiveDigits[0])
		parm2=int(instructionAsFiveDigits[1])
		parm1=int(instructionAsFiveDigits[2])
		opcode=int(instructionAsFiveDigits[3:5])
		retVal=[opcode,parm1,parm2,parm3]
		return retVal

	def evalOpPair(self, currentOp):
		""" Evaluages the two values for instruction like ADD, MUL
		Returns the two values as a list pair
		"""
		debug_BranchEval = False
		if debug_BranchEval:
			print("         evalOpPair: currentOp =",currentOp)
		val1 = self.dealWithOp(currentOp,1)
		val2 = self.dealWithOp(currentOp,2)
		return[val1,val2]
	
	def dealWithOp(self,currentOp,offset):
		""" Single place to interpret opcodes which read program memory
		Input the opcode field and the offset to the correct opcode field
		"""
		debug_dealWithOp = False
		if currentOp[offset] == 0:	# position mode
			val = self.programMemory[self.programMemory[self.programCounter+offset]]
			if debug_dealWithOp:
				print("         dealWithOp: Position Mode Parm",offset,"pos :",self.programCounter+offset,"value =",val)
		elif currentOp[offset] == 1:	# immediate mode
			val = self.programMemory[self.programCounter+offset]
			if debug_dealWithOp:
				print("         dealWithOp: Immediate Mode parm",offset,": value =",val)
		elif currentOp[offset] == 2:	# relative mode
			val = self.programMemory[self.programMemory[self.programCounter+offset] + self.relativeBaseRegister]
			if debug_dealWithOp:
				print("         dealWithOp: Relative Mode parm",offset,": value =",val)
		else:
			assert False,"dealWithOp: WTF-dealWithOp"
		return val
	
	def writeOpResult(self,opcode,opOffset,val):
#		debug_writeOpResult = True
		debug_writeOpResult = False
		if opcode[opOffset] == 0:
			self.programMemory[self.programMemory[self.programCounter+opOffset]] = val
			if debug_writeOpResult:
				print("writeOpResult: (position mode), val =",val,"to loc =",self.programMemory[self.programCounter+opOffset])
		elif opcode[opOffset] == 1:
			self.programMemory[self.programCounter+opOffset] = val
			if debug_writeOpResult:
				print("writeOpResult: (immediate mode), val =",val,"to loc =",self.programCounter+opOffset)
		elif opcode[opOffset] == 2:
			self.programMemory[self.programMemory[self.programCounter+opOffset] + self.relativeBaseRegister] = val
			if debug_writeOpResult:
				print("writeOpResult: (relative mode), val =",val,"to loc =",self.programMemory[self.programCounter+opOffset] + self.relativeBaseRegister)
	
	def runCPU(self):
		outputPacketSize = 3
#		debug_runCPU = True
		debug_runCPU = False
		while(1):
			currentOp = self.extractFieldsFromInstruction(self.programMemory[self.programCounter])
			if currentOp[0] == 1:		# Addition Operator
				if debug_runCPU:
					print("PC =",self.programCounter,"ADD Opcode = ",currentOp," ",end='')
				result = self.dealWithOp(currentOp,1) + self.dealWithOp(currentOp,2)
				if debug_runCPU:
					print(self.dealWithOp(currentOp,1),"+",self.dealWithOp(currentOp,2),"=",result)
				self.writeOpResult(currentOp,3,result)
				self.programCounter = self.programCounter + 4
			elif currentOp[0] == 2:		# Multiplication Operator
				if debug_runCPU:
					print("PC =",self.programCounter,"MUL Opcode = ",currentOp," ",end='')
				result = self.dealWithOp(currentOp,1) * self.dealWithOp(currentOp,2)
				if debug_runCPU:
					print(self.dealWithOp(currentOp,1),"*",self.dealWithOp(currentOp,2),"=",result)
				self.writeOpResult(currentOp,3,result)
				self.programCounter = self.programCounter + 4
			elif currentOp[0] == 3:		# Input Operator
				debug_CPUInput = False
#				debug_CPUInput = True
				if debug_runCPU or debug_CPUInput:
					print("PC =",self.programCounter,"INP Opcode = ",currentOp,end='')
				if len(self.inputQueue) == 0:
					if debug_runCPU or debug_CPUInput:
						print(" - Return for input value")
					self.setProgState('waitForInput')
					return
				else:
					if debug_runCPU or debug_CPUInput:
						print(" value =",self.inputQueue[0])
					result = self.inputQueue[0]
					self.writeOpResult(currentOp,1,result)
					del self.inputQueue[0]	 # Empty the input queue
				self.setProgState('inputWasRead')
				self.programCounter = self.programCounter + 2
			elif currentOp[0] == 4:		# Output Operator
				debug_CPUOutput = False
#				debug_CPUOutput = True
				val1 = self.dealWithOp(currentOp,1)
				if debug_runCPU or debug_CPUOutput:
					print("PC =",self.programCounter,"OUT Opcode = ",currentOp,end='')
					print(" value =",val1)
				self.outputQueue.append(val1)
				self.programCounter = self.programCounter + 2
				self.setProgState('outputReady')
				if len(self.outputQueue) == outputPacketSize:
					return
			elif currentOp[0] == 5:		# Jump if true
				if self.dealWithOp(currentOp,1) != 0:
#					self.programCounter = self.dealWithOp(currentOp,1)
					self.programCounter = self.dealWithOp(currentOp,2)
					if debug_runCPU:
						print("PC =",self.programCounter,"JIT Opcode = ",currentOp,"Branch taken")
				else:
					self.programCounter = self.programCounter + 3		
					if debug_runCPU:
						print("PC =",self.programCounter,"JIT Opcode = ",currentOp,"Branch not taken")
			elif currentOp[0] == 6:		# Jump if false
				if self.dealWithOp(currentOp,1) == 0:
#					self.programCounter = self.dealWithOp(currentOp,1)
					self.programCounter = self.dealWithOp(currentOp,2)
					if debug_runCPU:
						print("PC =",self.programCounter,"JIT Opcode = ",currentOp,"Branch taken")
				else:
					self.programCounter = self.programCounter + 3		
					if debug_runCPU:
						print("PC =",self.programCounter,"JIT currentOp",currentOp,"Branch not taken")
			elif currentOp[0] == 7:		# Evaluate if less-than
				valPair = self.evalOpPair(currentOp)
				pos = self.programMemory[self.programCounter+3]
				if valPair[0] < valPair[1]:
					result = 1
					if debug_runCPU:
						print("PC =",self.programCounter,"ELT Opcode = ",currentOp,valPair[0],"less than =",valPair[1],"True")
				else:
					result = 0
					if debug_runCPU:
						print("PC =",self.programCounter,"ELT Opcode = ",currentOp,valPair[0],"less than =",valPair[1],"False")
				self.writeOpResult(currentOp,3,result)
				self.programCounter = self.programCounter + 4
			elif currentOp[0] == 8:		# Evaluate if equal
				valPair = self.evalOpPair(currentOp)
				pos = self.programMemory[self.programCounter+3]
				if valPair[0] == valPair[1]:
					result = 1
					if debug_runCPU:
						print("PC =",self.programCounter,"EEQ does",valPair[0],"equal =",valPair[1],"True")
				else:
					result = 0
					if debug_runCPU:
						print("PC =",self.programCounter,"EEQ does",valPair[0],"equal =",valPair[1],"False")
				self.writeOpResult(currentOp,3,result)
				self.programCounter = self.programCounter + 4
			elif currentOp[0] == 9:		# Sets relative base register value
				if debug_runCPU:
					print("PC =",self.programCounter,"SBR Opcode = ",currentOp," ",end='')
				self.relativeBaseRegister += self.dealWithOp(currentOp,1)
				if debug_runCPU:
					print("self.relativeBaseRegister =",self.relativeBaseRegister)
				self.programCounter = self.programCounter + 2
			elif currentOp[0] == 99:
				if debug_runCPU:
					print("PC =",self.programCounter,"END Opcode = ",currentOp)
				self.progState = 'progDone'
				return 'Done'
			else:
				print("PC =",self.programCounter,"UNX Opcode = ",currentOp)
				print("error - unexpected opcode", currentOp[0])
				exit()
		assert False,"Unexpected exit of the CPU"

def allInputQueuesEmpty():
	allQueuesEmpty = True
	for cpuNumber in xrange(50):
		if CPUs[cpuNumber].getInputQueueLength() >= 2:
			return False
	return True

debugAll = False

#debug_main = True
debug_main = False

lastPacketValue = [-1,-1]
# Spawn 50 CPUs
CPUs = []
cpuRunning = []
packetVals = []
xVal = -1
yVal = -1
natX = -1
natY = -1
gotNATPacket = False
for cpuNumber in xrange(50):
	CPUs.append(CPU())
	# Feed the CPU its node number
	CPUs[cpuNumber].inputQueue.append(cpuNumber)
	cpuRunning.append(True)
while True in cpuRunning:
	if allInputQueuesEmpty() and gotNATPacket:
		if debug_main:
			print("Got NAT packet and all queues are empty")
		CPUs[0].inputQueue.append(natX)
		CPUs[0].inputQueue.append(natY)
		lastPacketValue = [xVal,yVal]
		if lastPacketValue in packetVals:
			# print("packetVals",packetVals)
			# print("last packet value to NAT was",lastPacketValue)
			print("The first repeated Y value to NAT was",lastPacketValue[1])
			exit()
		packetVals.append(lastPacketValue)
#		gotNATPacket = False
	for cpuNumber in range(50):
		CPUs[cpuNumber].runCPU()
		state = CPUs[cpuNumber].getProgState()
		if debug_main:
			print("CPU Number",cpuNumber,"state",state)
		if state == 'progDone':
			cpuRunning[cpuNumber] = False
		elif state == 'waitForInput' and CPUs[cpuNumber].getInputQueueLength() == 0:
			CPUs[cpuNumber].inputQueue.append(-1)			# Nothing in the queue so send -1
		if state == 'outputReady' and CPUs[cpuNumber].getOutputQueueLength() != 0:
			if debug_main:
				print("len of outputQueue =",len(CPUs[cpuNumber].outputQueue))
			cpuNum = CPUs[cpuNumber].outputQueue[0]
			xVal = CPUs[cpuNumber].outputQueue[1]
			yVal = CPUs[cpuNumber].outputQueue[2]
			if cpuNum < 255:
				CPUs[cpuNum].inputQueue.append(xVal)
				CPUs[cpuNum].inputQueue.append(yVal)
				del CPUs[cpuNumber].outputQueue[2]
				del CPUs[cpuNumber].outputQueue[1]
				del CPUs[cpuNumber].outputQueue[0]
			elif cpuNum == 255:
				# print("Got a packet for the NAT")
				# print("xVal",xVal)
				# print("yVal",yVal)
				natX = xVal
				natY = yVal
				del CPUs[cpuNumber].outputQueue[2]
				del CPUs[cpuNumber].outputQueue[1]
				del CPUs[cpuNumber].outputQueue[0]
				gotNATPacket = True
