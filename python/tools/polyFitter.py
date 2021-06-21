#!/usr/local/bin/python3.8
# polyFitter.py
# 6/21/2021
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# This script reads in a csv file containing calibration data and
# fits a Polynomial Series to it.

from matplotlib import pyplot as plt
from polyFit import polyFit
import numpy as np
import sys
import csv
import os

### How to use ################################################################
# Run this script with the following command options:
#   deg=#           Where # is the degree of fit. If not given, default is 5.
#   test=on         This allows the user to enter test points one at a time and 
#                   displays the calibrated result. enter 'q' to exit
#   plot=on         This plots the data, the fit, and test points if given.   
#   file=FILEPATH   This is the path to the calibration data file.

# The calibration data file should be a CSV in the following format:
#
#   RAW_VALUE_1,TEMPERATURE_1
#   RAW_VALUE_2,TEMPERATURE_2
#           ...
#   RAW_VALUE_N,TEMPERATURE_N
# 
# The script will output the polynomial coefficients in order of low -> high.
###############################################################################

def create_2d_plot(dataList1, dataList2, dataList3=None, fit_x=None, fit_y=None, poly=None):
    """
    Uses the supplied data to create a 2D plot.

    Input: 
    - dataList      List of coordinates (1, 2, or 3)
    - fit_x         polynomial fit x values
    - fit_y         polynomial fit y values

    Output:
    """
    xData1 = []
    yData1 = []
    for point in dataList1:
        xData1.append(point[0])
        yData1.append(point[1])
        
    plt.plot(xData1, yData1, '-o', color='blue')

    xData2 = []
    yData2 = []
    for point in dataList2:
        xData2.append(point[0])
        yData2.append(point[1])
        
    plt.plot(xData2, yData2, '-+', color='red')

    if dataList3 != None:
        xData3 = []
        yData3 = []
        for point in dataList3:
            xData3.append(point[0])
            yData3.append(point[1])
            
        plt.plot(xData3, yData3, '-^', color='green')
        plt.legend(['calibration data', 'test fit', 'user test points'])
    else:
        plt.legend(['calibration data', 'test fit'])

    plt.title('Temperature vs Sensor Units')
    plt.ylabel('Temperature')
    plt.xlabel('Sensor Units')

    return plt

def get_data(fileName):
    """
    Reads in a CSV file containing temperatures and sensor units
    
    CSV should be of format:
        float,float

    Input:
    - fileName  Filename of the CSV file, ending in .csv

    Output:
    - data      List of calibration data
    """

    # parse the CSV file
    with open(fileName, 'rt', encoding='utf-8-sig') as csvfile:
        data = [(float(temp), float(sens)) 
                for temp, sens in csv.reader(csvfile, delimiter= ',')]

    return data


if __name__ == "__main__":
    filePath = None
    degree = 5
    test = 'off'
    plot = 'off'

    for n in range(len(sys.argv)):
        try:
            if 'file=' in sys.argv[n]:
                filePath = sys.argv[n].split('=')[1]

            elif 'deg=' in sys.argv[n]:
                degree = int(sys.argv[n].split('=')[1])

            elif 'plot=' in sys.argv[n]:
                plot = sys.argv[n].split('=')[1]

            elif 'test=' in sys.argv[n]:
                test = sys.argv[n].split('=')[1]

        except Exception as e:
                sys.exit(f'ERROR: {e}')

    if filePath == None:
        sys.exit('ERROR: No calibration data supplied.')

    if filePath[0] == '~':
        filePath = os.path.expanduser('~')+filePath[1:]

    if filePath[len(filePath)-4:] == '.csv':
        data = get_data(filePath)
        
        polyFit = polyFit(data, degree)
        print(f'coefficients(low->high)={polyFit.polyFit[0]}')

        testData = get_data(filePath)
        testResults = []

        ## Test each point by calculating temp with the Polynomial Fit
        for n in range(len(testData)):
            temp = polyFit.calib_t(testData[n][0])
            testResults.append([testData[n][0], temp])

        if test == 'on':
            testResults2 = []
            inTmp = ''
            while inTmp != 'q':
                inTmp = input(':')
                try:
                    tmp = float(inTmp)
                    calTmp = polyFit.calib_t(tmp)
                    print(f'={calTmp}')
                    testResults2.append([tmp, calTmp])
                except:
                    pass

        if plot == 'on':
            if test == 'on':
                plt = create_2d_plot(data, testResults, testResults2)
                plt.show()
            else:
                plt = create_2d_plot(data, testResults)
                plt.show()