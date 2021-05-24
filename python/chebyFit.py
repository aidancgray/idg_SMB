# chebyFit.py
# 5/19/2021
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# This is a class module for a Chebyshev Polynomial Fit
# Instantiate the object with chebyFit(data, deg) where the data is a 
# list of pairs and deg is the degree of the polynomial. If deg is not 
# specified, the largest degree possible before a Rank Warning is raised
# will be used. This usually results in a poor fit except for the exact
# points used in calibration, which will be right on. Personal testing
# has shown a degree of 10 to be very accurate.

import numpy as np
import numpy.polynomial.chebyshev as cheby
import math
import time
import warnings

class chebyFit():
    def __init__(self, data=None, deg=None, coeffs=None, zl=None, zu=None ):
        if data == None and coeffs != None and zl != None and zu != None:
            self.chebyFit = [coeffs, zl, zu]
        elif data != None and coeffs == None and zl == None and zu == None:
            self.xData, self.yData = self.__get_xy(data)
            self.chebyFit = self.__cheby_fit(deg)
        else:
            raise TypeError('If finding a new fit, only pass \'data\' and \'deg\' parameters. \
                            If creating a chebyFit object of a known fit, only pass \
                            \'coeffs\', \'zl\', \'zu\' parameters.')

    def __get_xy(self, dataList):
        xData = []
        yData = []
        
        for point in dataList:
            xData.append(point[0])
            yData.append(point[1])
            
        return xData, yData

    def __cheby_fit(self, deg):
        np.seterr(divide='raise')
        d = 0
        
        if deg == None:
            with warnings.catch_warnings():
                warnings.filterwarnings('error')
                try:
                    for n in range(100):
                        cheb = cheby.Chebyshev.fit(self.xData, self.yData, n, full=True)
                        d = n
                        time.sleep(0.1)
                except np.polynomial.polyutils.RankWarning:
                        pass
        else:
            cheb = cheby.Chebyshev.fit(self.xData, self.yData, deg, full=True)

        chebCoefs = cheb[0].coef
        ssreg = cheb[1][0][0]
        # print(f'r={ssreg}')

        ybar = np.sum(self.yData)/len(self.yData)
        # print(f'ybar={ybar}')
        sstot = np.sum((self.yData - ybar)**2)
        # print(f'sstot={sstot}')
        r2 = 1 - ssreg/sstot
        # print(f'r2={r2}')
        
        ZL = min(self.xData)
        ZU = max(self.xData)
        
        chebyFit = [chebCoefs, ZL, ZU]
        return chebyFit
        
    def calib_t(self, Z):
        chebCoefs = self.chebyFit[0]
        ZL = self.chebyFit[1]
        ZU = self.chebyFit[2]
        
        X = ((Z - ZL) - (ZU - Z)) / (ZU - ZL) 
        if abs(X) >= 1:
            return -1
            
        T = 0
        deg = len(chebCoefs)
        
        for n in range(deg):
            a = chebCoefs[n]
            
            if n == 0:
                tn = 1
            elif n == 1:
                tn = X
            else:
                tn = math.cos(n * math.acos(X))
                
            T = T + (a * tn)
            
        return T