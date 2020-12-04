"""
@Author: Arjun Ravikumar
@Purpose: To convert the given GPS data into KML file by removing redundant and error data
"""

import csv
import simplekml

class GPStoKML:

	"""
	init function of the class
	"""

	def __init__(self,inFile,outFile):
		print("Starting the convertion of GPS to KML",inFile,"to",outFile)

	"""
	To input data from the text file and format it
	"""

	def getInputFileData(self,fileName):
		inputfile = open(fileName, 'r',errors='ignore') 
		allpoints = []
		direction = []
		for line in inputfile:
			row = line.split(",")
			"""
			Initial screening of the data and some error formating for rmeoving junk data
			"""
			if row is None:
				continue
			if len(row) > 1 and 'GPRMC' in row[0]:
				if(self.checkIfDigit(row[3]) and self.checkIfDigit(row[5]) and self.checkIfDigit(row[7]) and self.checkIfDigit(row[8])):
					point = [0,0,0]
					point[1] = (float(row[3])/100) 
					point[1] = self.convertToDecimal(point[1])
					if(row[4] == "S"):
						point[1] *= -1
					point[0] = (float(row[5])/100)
					point[0] = self.convertToDecimal(point[0])
					if(row[6] == "W"):
						point[0] *= -1
					point[2] = float(row[7])
					allpoints.append(point.copy())
					direction.append(float(row[8]))
		inputfile.close()
		return allpoints,direction
	
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
	To remove the redudant data and data with error
	"""

	def removeRedundantandDataWithError(self,inputData,direction):
		outputData = [inputData[0]]
		locIndex = 1
		while (locIndex < len(inputData)):
			count = 0
			"""
			for minimizing data when the car is stopped or stationary and will also reduce the Dilution of Precision
			"""
			while(locIndex < len(inputData) and (inputData[locIndex-1][2] < 1) and (inputData[locIndex][2] < 1)):
				if((inputData[locIndex-1][2] > 0) and (inputData[locIndex][2] > 0)):
					count+=1
					if(count % 1000 == 0 and (self.checkforAnomaly(outputData[len(outputData)-1],inputData[locIndex]))):
						outputData.append(inputData[locIndex])
				locIndex+=1
			if(locIndex < len(inputData) and (self.checkforAnomaly(outputData[len(outputData)-1],inputData[locIndex]))):
				outputData.append(inputData[locIndex])
			count = 0
			"""
			for minimizing data when the car is travelling in a straight line skipping points in between 
			"""
			while(locIndex < len(inputData) and (abs(direction[locIndex-1] - direction[locIndex]) < 0.1) \
				and inputData[locIndex][2] > 1):
				locIndex+=1
				count+=1
				if(count % 100 == 0 and (self.checkforAnomaly(outputData[len(outputData)-1],inputData[locIndex]))):
					outputData.append(inputData[locIndex])
			"""
			for reducing anomaly points; here the data is always checked with the previous data recoreded
			"""
			while (locIndex < len(inputData) and (self.checkforAnomaly(outputData[len(outputData)-1],inputData[locIndex]) == False)):
				locIndex+=1
			locIndex+=1
		print("Original file data length",len(inputData))
		print("Reduced file data length",len(outputData))
		return outputData
	
	"""
	To check for anomalies if anomaly will return false else true
	"""

	def checkforAnomaly(self,point1,point2):
		if((abs(point1[1] - point2[1]) > 0.02) and (abs(point1[0] - point2[0]) > 0.03)):
			return False
		return True

	"""
	To save the points to the KML file
	"""

	def saveKmlFile(self,fileName,data):
		"""
		giving line colour and thickness to make it stand out better
		"""
		kml=simplekml.Kml()
		line = kml.newlinestring(coords=data)
		line.style.linestyle.color = simplekml.Color.cyan
		line.style.linestyle.width = 10
		kml.save(fileName)
	
	"""
	To start removing redundant points and clean the data
	"""

	def startConvertingToKML(self,inputFName,outputFName):
		preProcessedPoints,direction = self.getInputFileData(inputFName)
		formatedPoints = self.removeRedundantandDataWithError(preProcessedPoints,direction)
		self.saveKmlFile(outputFName,formatedPoints)