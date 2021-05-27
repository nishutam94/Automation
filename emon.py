import time 
import os, sys
import argparse
from argparse import ArgumentParser
class emon():
	def __init__(self, args):
		'''
			emonPath -> EMON installation root folder (where sep_vars.sh is located)
			resultsPath -> Path to store output. If not given root/emon/results is used as default. 
			input -> CPU MSR/event file 
			measTime -> Amount of time in seconds. 

			Usage:
				import emon
				emon = emon(<results_path>, <events_input_file>, <measurement_time_in_s>)
				emon.startSampling()

		'''
		self.args = args
		self.results = self.args.resultsPath 
		self.input = self.args.input
		self.emonPath = self.args.emonPath
		self.measTime = self.args.measTime

		os.system("mkdir %s"%(self.results))
		if self.results == None:
			self.results = "/root/emon/results"
			try: 
				os.system("mkdir /root/emon/results")
			except: os.system("mkdir /root/emon/")
			try:
				os.system("mkdir /root/emon/results")
			except: pass
		
		else:
			if os.path.isdir(self.results) == True:
				pass
			else:
				print "Results path given does not exists, creating"
				self.results = "/root/emon/results"

		#Adding date and time to the results
		timeMark = time.struct_time(time.gmtime())
		timeMark = "%s_%s_%s___%s_%s_%s"%(timeMark.tm_year, timeMark.tm_mon, timeMark.tm_mday, timeMark.tm_hour, timeMark.tm_min, timeMark.tm_sec)
		self.results = self.results + "/" + timeMark
		os.system("mkdir %s"%(self.results))

		#Validating EMON path
		if os.path.isfile(self.emonPath + "/sep_vars.sh"):
			pass
		else:
			print "The EMON path provided is incorrect, exiting script"
			sys.exit()

		#Validating input file
		if os.path.isfile(self.emonPath + "/"+self.input):
			self.input = self.emonPath + "/"+self.input

			print(self.input)
		else:
			print "Input file not located @: %s, please place a copy there"%(self.emonPath)
			sys.exit()

		#Executing
		self.executionFlow()



	def startSampling(self):
		iteration = 0
		lapsedTime = 0
		#Information coming form -v and -M is needed by EDP post-processing tool 
		#The next command is to get actual data. 
		iniTime = time.time()	
		#Sourcing EMON
		cmd = "source" + " " + self.emonPath + "/sep_vars.sh" + " &> %s/emonInstall.log" %(self.emonPath)
		#debug 
		#print cmd
		while lapsedTime < self.measTime:
			emonv = "%s; emon -v >> %s/emon-v_%s.dat"%(cmd, self.results, iteration)
			emonM = "%s; emon -M >> %s/emon-m_%s.dat"%(cmd, self.results, iteration)
			emonR = "%s; emon -i %s >> %s/emon_%s.out"%(cmd, self.input, self.results, iteration)
			#print emonv
			#print emonM
			#print emonR
			os.system(emonv)
			os.system(emonM)
			os.system(emonR)
			endTime = time.time()
			lapsedTime = endTime - iniTime
			iteration += 1
		print "EMON data collected for: ", self.measTime

	def installEmon(self):
		print "\nSetting EMON..."
		os.chdir(self.emonPath + "/sepdk/src")
		cmd = "./build-driver -ni &> %s/emonInstall.log" %(self.emonPath)
		os.system(cmd)
		cmd = "./insmod-sep -g root &> %s/emonInstall.log" %(self.emonPath)
		os.system(cmd)

	def executionFlow(self):
		self.installEmon()
		self.startSampling()


if __name__ == "__main__":
	parser = ArgumentParser()
	parser.add_argument('--emonPath', type=str, default='/root/emon/sep', help="directory where emon installed")
	parser.add_argument("-o",'--resultsPath', type=str, default="/root/emon/results2", help="output directory path")
	parser.add_argument('--input', type=str, default='spr-2s-events.txt',help="path configuration emon file")
	parser.add_argument('--measTime', type=int, default=30,help="time to coplete emon")
	args = parser.parse_args()
	emon(args)