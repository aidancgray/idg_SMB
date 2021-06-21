# polyFit.py
# 6/21/2021
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# This is a class module for a Polynomial Fit.
# Instantiate the object with polyFit(data, deg) where the data is a 
# list of pairs and deg is the degree of the polynomial. If deg is not 
# specified, the largest degree possible before a Rank Warning is raised
# will be used. This usually results in a poor fit except for the exact
# points used in calibration, which will be right on. Personal testing
# has shown a degree of 10 to be very accurate.

import numpy as np
import numpy.polynomial.polynomial as poly
import math
import time
import warnings

class polyFit():
    def __init__(self, data=None, deg=None, coeffs=None, zl=None, zu=None ):
        if data == None and coeffs != None and zl != None and zu != None:
            self.polyFit = [coeffs, zl, zu]
        elif data != None and coeffs == None and zl == None and zu == None:
            self.xData, self.yData = self.__get_xy(data)
            self.polyFit = self.__poly_fit(deg)
        else:
            raise TypeError('If finding a new fit, only pass \'data\' and \'deg\' parameters. \
                            If creating a polyFit object of a known fit, only pass \
                            \'coeffs\', \'zl\', \'zu\' parameters.')

    def __get_xy(self, dataList):
        xData = []
        yData = []
        
        for point in dataList:
            xData.append(point[0])
            yData.append(point[1])
            
        return xData, yData

    def __poly_fit(self, deg):
        np.seterr(divide='raise')
        
        if deg == None:
            d = 0
            r2 = 0

            with warnings.catch_warnings():
                warnings.filterwarnings('error')
                try:
                    for n in range(5):
                        poltmp = poly.polyfit(self.xData, self.yData, n, full=True)
                        
                        ssreg = poltmp[1][0][0]
                        ybar = np.sum(self.yData)/len(self.yData)
                        sstot = np.sum((self.yData - ybar)**2)
                        r2tmp = 1 - ssreg/sstot
                        # print(f'n={n}')
                        # print(f'r2tmp={r2tmp}')
                        # print(f'----------')

                        if r2tmp > r2:
                            d = n
                            pol = poltmp

                        time.sleep(0.1)
                except np.polynomial.polyutils.RankWarning:
                        pass

        else:
            pol = poly.polyfit(self.xData, self.yData, deg, full=True)
        
        polCoefs = pol[0]
        
        ZL = min(self.xData)
        ZU = max(self.xData)
        
        polyFit = [polCoefs, ZL, ZU]
        return polyFit
        
    def calib_t(self, Z):
        polCoefs = self.polyFit[0]
            
        T = 0
        deg = len(polCoefs)
        
        for n in range(deg):
            c = polCoefs[n]
                
            T = T + (c * (Z**n))
            
        return T# polyFit.py
# 6/21/2021
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# This is a class module for a Polynomial Fit.
# Instantiate the object with polyFit(data, deg) where the data is a 
# list of pairs and deg is the degree of the polynomial. If deg is not 
# specified, the largest degree possible before a Rank Warning is raised
# will be used. This usually results in a poor fit except for the exact
# points used in calibration, which will be right on. Personal testing
# has shown a degree of 10 to be very accurate.

import numpy as np
import numpy.polynomial.polynomial as poly
import math
import time
import warnings

class polyFit():
    def __init__(self, data=None, deg=None, coeffs=None, zl=None, zu=None ):
        if data == None and coeffs != None and zl != None and zu != None:
            self.polyFit = [coeffs, zl, zu]
        elif data != None and coeffs == None and zl == None and zu == None:
            self.xData, self.yData = self.__get_xy(data)
            self.polyFit = self.__poly_fit(deg)
        else:
            raise TypeError('If finding a new fit, only pass \'data\' and \'deg\' parameters. \
                            If creating a polyFit object of a known fit, only pass \
                            \'coeffs\', \'zl\', \'zu\' parameters.')

    def __get_xy(self, dataList):
        xData = []
        yData = []
        
        for point in dataList:
            xData.append(point[0])
            yData.append(point[1])
            
        return xData, yData

    def __poly_fit(self, deg):
        np.seterr(divide='raise')
        
        if deg == None:
            d = 0
            r2 = 0

            with warnings.catch_warnings():
                warnings.filterwarnings('error')
                try:
                    for n in range(5):
                        poltmp = poly.polyfit(self.xData, self.yData, n, full=True)
                        
                        ssreg = poltmp[1][0][0]
                        ybar = np.sum(self.yData)/len(self.yData)
                        sstot = np.sum((self.yData - ybar)**2)
                        r2tmp = 1 - ssreg/sstot
                        # print(f'n={n}')
                        # print(f'r2tmp={r2tmp}')
                        # print(f'----------')

                        if r2tmp > r2:
                            d = n
                            pol = poltmp

                        time.sleep(0.1)
                except np.polynomial.polyutils.RankWarning:
                        pass

        else:
            pol = poly.polyfit(self.xData, self.yData, deg, full=True)
        
        polCoefs = pol[0]
        
        ZL = min(self.xData)
        ZU = max(self.xData)
        
        polyFit = [polCoefs, ZL, ZU]
        return polyFit
        
    def calib_t(self, Z):
        polCoefs = self.polyFit[0]
            
        T = 0
        deg = len(polCoefs)
        
        for n in range(deg):
            c = polCoefs[n]
                
            T = T + (c * (Z**n))
            
        return T