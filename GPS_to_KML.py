"""
@Author: Arjun Ravikumar
@Purpose: To call convert to GPS data to KML
"""

from convertGPStoKML import GPStoKML
import sys

"""
starts the execution to the cleaning the points
"""

def main():
	inputFile = sys.argv[1]
	outputFile = sys.argv[2]
	convData = GPStoKML(inputFile,outputFile)
	convData.startConvertingToKML(inputFile,outputFile)

main()