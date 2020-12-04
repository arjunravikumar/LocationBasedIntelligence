"""
@Author: Arjun Ravikumar
@Purpose: To extract the stop signs left and right turn and agglomerate the data from the given GPS data
"""

import csv
import simplekml
import os
from datetime import datetime
from Agglomeration import Agglomerate
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage

class GenerateCostMap:

	angleChange = 0
	stopSpeed = 0
	maxStopTime = 0
	minStopTime = 0
	leftTurnTime = 0
	rightTurnTime = 0
	TEST_MODE = False

	"""
	init function of the class
	"""
	
	def __init__(self):
		print("Starting To cluster points")
		self.angleChange = 60
		self.stopSpeed = 10.5
		self.maxStopTime = 120
		self.minStopTime = 10
		self.leftTurnTime = 10
		self.rightTurnTime = 8

	"""
	To input data from the text file and format it
	"""

	def getInputFileData(self,filePath):
		inputfile = open(filePath, 'r',errors='ignore') 
		allpoints = []
		for line in inputfile:
			row = line.split(",")
			"""
			Initial screening of the data and some error formating for rmeoving junk data
			"""
			if row is None:
				continue
			if len(row) > 1:
				if 'GPRMC' in row[0]:
					if(self.checkIfDigit(row[3]) and self.checkIfDigit(row[5]) and self.checkIfDigit(row[7]) and self.checkIfDigit(row[8])):
						point = [0,0,0,0,0]
						point[0] = (float(row[5])/100)
						point[0] = self.convertToDecimal(point[0])
						if(row[6] == "W"):
							point[0] *= -1
						point[1] = (float(row[3])/100) 
						point[1] = self.convertToDecimal(point[1])
						if(row[4] == "S"):
							point[1] *= -1
						point[2] = float(row[7])
						point[3] = row[1]
						point[4] = float(row[8])
						allpoints.append(point.copy())
		inputfile.close()
		return allpoints
	
	"""
	Convert longitude and lattitude from degree to decimal
	"""

	def convertToDecimal(self,num):
		minute = num - int(num)
		minute = minute * (5/3)
		num = int(num) + minute
		return num

	"""
	Convert the string in digit
	"""

	def checkIfDigit(self,strNum):
		return strNum.replace('.', '', 1).isdigit()

	"""
	Get the difference of the times in seconds
	"""

	def getTheTimeDifferenceInSeconds(self,time1,time2):
		time1 = time1.split(".")[0]
		time2 = time2.split(".")[0]
		time1 = ":".join([time1[timeStr:timeStr+2] for timeStr in range(0,len(time1),2)])
		time2 = ":".join([time2[timeStr:timeStr+2] for timeStr in range(0,len(time2),2)])
		FMT = '%H:%M:%S'
		return (datetime.strptime(time2, FMT) - datetime.strptime(time1, FMT)).total_seconds()

	"""
	To classify the points to stop signal, left turn and right turn
	"""

	def classifyPoints(self,points,stopSignal,leftTurn,rightTurn):
		"""
		0 - longitude
		1 - latitude
		2 - speed
		3 - time
		4 - direction
		"""	
		locIndex = 1
		while (locIndex < len(points)):
			"""
			conditions for classifying a sign or traffic light
			"""
			start = locIndex-1
			end = locIndex
			while((end < len(points)) and (points[start][2] >= self.stopSpeed) and (points[end-1][2] >= points[end][2])):
				end+=1
			timeElapsed = self.getTheTimeDifferenceInSeconds(points[start][3],points[end-1][3])
			if(timeElapsed > self.minStopTime and points[start][2] >= self.stopSpeed and (points[end][2] <= self.stopSpeed) and \
				(points[start][2] >= points[end-1][2]) and timeElapsed < self.maxStopTime):
				stopSignal.append(points[end-1][:2])
				locIndex = end-1
			locIndex+=1

		locIndex = 1
		while (locIndex < len(points)):
			"""
			conditions for classifying a left turn
			"""
			start = locIndex-1
			end = locIndex
			while((end < len(points)) and (self.changeInAngle(points[end-1][4],points[end][4]) < 0) and 
				(points[end-1][2] >= 1 and points[end][2] >= 1)):
				end+=1
			timeElapsed = self.getTheTimeDifferenceInSeconds(points[start][3],points[end-1][3])
			if(end < len(points) and self.changeInAngle(points[start][4],points[end][4])<(-self.angleChange) and 
				(points[start][2] >= 1 and points[end][2] >= 1) and (timeElapsed<self.leftTurnTime)):
				leftTurn.append(points[(start+end-1)//2][:2])
				locIndex = end-1
			"""
			conditions for classifying a right turn
			"""
			start = locIndex-1
			end = locIndex
			while((end < len(points)) and (self.changeInAngle(points[end-1][4],points[end][4]) > 0) and 
				(points[end-1][2] >= 1 and points[end][2] >= 1)):
				end+=1
			timeElapsed = self.getTheTimeDifferenceInSeconds(points[start][3],points[end-1][3])
			if(end < len(points) and (self.changeInAngle(points[start][4],points[end][4])>self.angleChange) and 
				(points[start][2] >= 1 and points[end][2] >= 1) and (timeElapsed<self.rightTurnTime)):
				rightTurn.append(points[(start+end-1)//2][:2])
				locIndex = end-1
			locIndex += 1
		return stopSignal,leftTurn,rightTurn
	
	"""
	To find the change in angle between the 2 points
	"""

	def changeInAngle(self,a,b):
		d = abs(a - b) % 360 
		if(d > 180):
			r = 360 - d
		else:
			r = d
		if (a - b >= 0 and a - b <= 180)  or (a - b <=-180 and a- b>= -360):
			r *= 1
		else:
			r *= -1
		return r
	
	"""
	To save the points to the KML file
	"""

	def saveKmlFile(self,fileName,stopSignal,leftTurn,rightTurn):
		"""
		giving points separate images for better distinction between points
		"""
		kml=simplekml.Kml()
		styleRight = simplekml.Style()
		styleRight.labelstyle.color = simplekml.Color.red
		styleRight.labelstyle.scale = 2
		styleRight.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/paddle/1.png"
		styleStop = simplekml.Style()
		styleStop.labelstyle.color = simplekml.Color.cyan
		styleStop.labelstyle.scale = 2
		styleStop.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"
		for dataIndex in range(len(stopSignal)):
			pnt = kml.newpoint(name='StopSignal: {0}'.format(dataIndex))
			pnt.coords = [stopSignal[dataIndex][:2]] 
			pnt.style = styleStop
		for dataIndex in range(len(leftTurn)):
			pnt = kml.newpoint(name='LeftTurn: {0}'.format(dataIndex))
			pnt.coords = [leftTurn[dataIndex][:2]] 
		for dataIndex in range(len(rightTurn)):
			pnt = kml.newpoint(name='RightTurn: {0}'.format(dataIndex))
			pnt.coords = [rightTurn[dataIndex][:2]] 
			pnt.style = styleRight
		kml.save(fileName)

	"""
	To plot the dendogram if necessary
	"""

	def plotDendo(self,X,img1Name,img2Name):
		linked = linkage(X, 'single')
		plt.figure(figsize=(20, 14))
		dendrogram(linked,p=100,truncate_mode = "level")
		plt.savefig(img1Name)
		labels = range(1, 11)
		plt.figure(figsize=(20, 14))
		plt.subplots_adjust(bottom=0.1)
		plt.scatter([lng[0] for lng in X],[lng[1] for lng in X], label='True Position',alpha = 0.5)
		plt.savefig(img2Name)
		plt.close()

	"""
	To call the agglomerate function to agglomerate the points
	"""

	def agglomerateData(self,data,typeOfPoints):
		aggloObject = Agglomerate(typeOfPoints)
		aggloObject.setData(data,["longitude","latitude"])
		clusterCenters = aggloObject.startAgglomeration()
		return clusterCenters

	"""
	To start clustering the points
	"""

	def startClusteringPoints(self,inputDirectory,outputFileName):
		stopSignal = []
		leftTurn = []
		rightTurn = []
		
		print("\nInputting all Data")
		totalFiles = os.listdir(inputDirectory)
		countFiles = 0
		for filename in totalFiles:
			if filename.endswith(".txt"):
				filePath = os.path.join(inputDirectory, filename)
				points = self.getInputFileData(filePath)
				stopSignal,leftTurn,rightTurn = self.classifyPoints(points,stopSignal,leftTurn,rightTurn)
			countFiles+=1
			"""
			for showing the progress in the loading of data from csv
			"""
			print("Input loading progress {:2.1%}".format(countFiles / len(totalFiles)), end="\r")
		print("Input loading progress {:2.1%}".format(countFiles / len(totalFiles)))
		print("Stop Signal count before Agglomeration",len(stopSignal))
		print("Left Turn count before Agglomeration",len(leftTurn))
		print("Right Turn count before Agglomeration",len(rightTurn))
		if(self.TEST_MODE == True):
			self.plotDendo(stopSignal,"StopDendo.png","StopCluster.png")
			self.plotDendo(leftTurn,"LeftDendo.png","LeftCluster.png")
			self.plotDendo(rightTurn,"RightDendo.png","RightCluster.png")
		print("\nStarting Agglomeration")
		print("\nAgglomerating Stop Signals (0/3)")
		stopSignalClusterCenters = self.agglomerateData(stopSignal,"stop signal")
		print("\nAgglomerating Left Turns (1/3)")
		leftTurnClusterCenters = self.agglomerateData(leftTurn,"left turn")
		print("\nAgglomerating Right Turns (2/3)")
		rightTurnClusterCenters = self.agglomerateData(rightTurn,"right turn")
		print("\nSaving the files to KML (3/3)")
		self.saveKmlFile(outputFileName,stopSignalClusterCenters,leftTurnClusterCenters,rightTurnClusterCenters)
		print("\nDone")


