"""
@Author: Arjun Ravikumar
@Purpose: To find the stop signals and left right turns
"""

from CostMapGenerator import GenerateCostMap
import sys

"""
starts the execution of the clustering of points
"""

def main():
	inputFilePath = sys.argv[1]
	outputFile = sys.argv[2]
	convData = GenerateCostMap()
	convData.startClusteringPoints(inputFilePath,outputFile)

main()