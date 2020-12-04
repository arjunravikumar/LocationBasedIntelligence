1) To run the GPS_to_KML file please give the input of the file name and the output filename as command line arguments when running for example -
python3 GPS_to_KML.py FILES_TO_WORK/2019_03_12__1423_30.txt OutputFiles/GPS_Path.kml 
	1a) This will take about 1 second for an average file to run.
	1b) It will output original file size and final formatted data size (number of data points)
	1c) Please keep convertGPStoKML.py also in the same folder as the GPS_to_KML file for running it.
2) To run the GPS_to_CostMap file please give the input of the folder path and the output filename as command line arguments when running for example -
python3 GPS_to_CostMap.py FILES_TO_WORK/ OutputFiles/GPS_Hazards.kml 
	2a) Please ensure the files in the input folder are *.txt format
	2b) The program will take 60mins to 70mins for running on the FILES_TO_WORK/ folder
	2c) The program will show to progress of input and agglomeration progress through the steps.
	2d) Please keep CostMapGenerator.py and Agglomeration.py also in the same folder as the GPS_to_CostMap file for running it.
	2e) Please change the variable TEST_MODE to False if there no need to see the dendogram and scatter plot.
	2f) The program will show the number of points initally before clustering and the number of clusters finally also.
3) The output kml files are present in OutputFiles folder.