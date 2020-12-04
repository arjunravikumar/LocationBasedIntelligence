"""
@Author: Arjun Ravikumar
@Purpose: To find the best cluster count and then agglomerate the data
"""

import numpy as np
import sys
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

'''
Global variables
'''

class Agglomerate:
	columnsArray = {}
	csvData = {}
	clusters = []
	clusterList = []
	clusterCount = 200
	
	"""
	init function of the class
	"""

	def __init__(self,typeOfPoints):
		print("Starting to cluster the "+typeOfPoints+" points")
		self.columnsArray = {}
		self.csvData = {}
		self.clusters = []
		self.clusterList = []

	'''
	To find the number of clusters using kmeans and silhoutte score
	'''

	def findTheNumberOfCluster(self,data):
		startRange = (len(data)//100)
		endRange = (len(data)//5)
		if(startRange == 0):
			startRange = startRange+2
		if(endRange <= startRange):
			endRange = startRange+2
		if(endRange > len(data)):
			endRange = len(data)
		range_n_clusters = range(startRange, endRange)
		silhouetteAvgArr = [0 for i in range(endRange)]
		for n_clusters in range_n_clusters:
		    clusterer = KMeans(n_clusters=n_clusters, random_state=100)
		    cluster_labels = clusterer.fit_predict(data)
		    silhouette_avg = silhouette_score(data, cluster_labels)
		    silhouetteAvgArr[n_clusters] = silhouette_avg
		return silhouetteAvgArr.index(max(silhouetteAvgArr))

	'''
	To calculate the eculidian distance
	'''

	def getEuclideanDistanct(self,guest1,guest2):
		euclideanDistance =  np.sqrt(np.sum(np.square(np.array(guest1) - np.array(guest2))))
		return euclideanDistance

	'''
	finds the initial distance between all the nodes and populates the distancedictonary
	'''

	def findDistanceBetweenGuests(self,aggloDict):
		aggloKeys = aggloDict.keys()
		sorted(aggloKeys)
		distanceDict = {}
		for key in aggloKeys:
			distanceDict[key] = {}
		for key1 in aggloKeys:
			for key2 in aggloKeys:
				if(key1 == key2):
					dist = float("inf")
				else:
					dist = self.getEuclideanDistanct(aggloDict[key1],aggloDict[key2])
				distanceDict[key1][key2] = dist
		return distanceDict

	'''
	finds the minimum distance in the distance matrix
	'''

	def findMinDistance(self,distanceDict):
		lowestDistance = float("inf")
		closestGuests = [0,0]
		distKeys = distanceDict.keys()
		sorted (distKeys)
		for index1 in distKeys:
			for index2 in distKeys:
				if(lowestDistance > distanceDict[index1][index2]):
					lowestDistance = distanceDict[index1][index2]
					closestGuests[0] = index1
					closestGuests[1] = index2
		return closestGuests

	'''
	combines the nodes which has the least distance
	'''

	def combineTheGuests(self,aggloDict,closestGuests):
		aggloDict = self.removekey(aggloDict,closestGuests[0])
		aggloDict = self.removekey(aggloDict,closestGuests[1])
		aggloDict[",".join(closestGuests)] = self.getAverageOfLists(closestGuests)
		return aggloDict

	'''
	combines the nodes or node clusters which has the least distance between them
	'''

	def combineTheDistancesOfTheGuests(self,aggloDict,distanceDict,closestGuests):
		distanceDict = self.removekey(distanceDict,closestGuests[0])
		distanceDict = self.removekey(distanceDict,closestGuests[1])
		distKeys = distanceDict.keys()
		newPoint = self.getAverageOfLists(closestGuests)
		sorted (distKeys)
		for key in distKeys:
			distanceDict[key] = self.removekey(distanceDict[key],closestGuests[0])
			distanceDict[key] = self.removekey(distanceDict[key],closestGuests[1])
		newKey = ",".join(closestGuests)
		aggloDict = self.combineTheGuests(aggloDict,closestGuests)
		aggloKeys = aggloDict.keys()
		sorted(aggloKeys)
		distanceDict[newKey] = {}
		for key1 in aggloKeys:
			if(newKey == key1):
				dist = float("inf")
			else:
				dist = self.getEuclideanDistanct(aggloDict[key1],newPoint)
			distanceDict[newKey][key1] = dist
			distanceDict[key1][newKey] = dist
		return aggloDict,distanceDict

	'''
	returns the center of mass of all the nodes in the cluster
	'''

	def getAverageOfLists(self,closestGuests):
		points = []
		for guestIndex in range(0,len(closestGuests)):
			individualVals = closestGuests[guestIndex].split(",")
			for val in individualVals:
				points.append(val)
		newArr = [0 for dummy in range(len(self.csvData[points[0]]))]

		for pointIndex in range(len(points)):
			list1 = self.csvData[points[pointIndex]]
			newArr = [val1 + val2 for (val1, val2) in zip(newArr, list1)]
		for arrIndex in range(len(newArr)):
			newArr[arrIndex] = float(newArr[arrIndex]/len(points))
		return newArr.copy()

	'''
	for removing a key from the dictionary
	'''

	def removekey(self,d, key):
		r = dict(d)
		del r[key]
		return r

	'''
	The function to start the Agglomeration process this controls the number of clusters as well
	'''

	def startAgglomeration(self):
		aggloDict = self.csvData.copy()
		aggloDistMasterCopy = self.csvData.copy()
		distanceDict = self.findDistanceBetweenGuests(aggloDict)
		self.clusterList = [[str(val)] for val in range(0,len(distanceDict))]
		while(len(aggloDict) > self.clusterCount):
			closestGuests = self.findMinDistance(distanceDict)
			self.clusterList.append([closestGuests[0].split(","),closestGuests[1].split(",")])
			aggloDict,distanceDict = self.combineTheDistancesOfTheGuests(aggloDict,distanceDict,closestGuests)
		for key in aggloDict.keys():
			closestPoint = self.findTheClosestPoint(aggloDict[key],aggloDistMasterCopy,key)
			self.clusters.append(closestPoint)
		return self.clusters

	'''
	The function finds the closest point to the mean point from the agglomeration center
	'''

	def findTheClosestPoint(self,point,dictMaster,groupOfPoints):
		bestDist = float("inf")
		closestPoint = None
		for key in groupOfPoints.split(","):
			dist = self.getEuclideanDistanct(point,dictMaster[key])
			if(bestDist > dist):
				bestDist = dist
				closestPoint = dictMaster[key]
		return closestPoint

	'''
	The function to set the global variables
	'''

	def setData(self,csvDataArr,attributeData):
		self.clusterCount = self.findTheNumberOfCluster(csvDataArr)
		print("Number of clusters: ",self.clusterCount)
		for row in range(0,len(csvDataArr)):
			self.csvData[str(row)] = csvDataArr[row]
		self.columnsArray = attributeData