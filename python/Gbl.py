# Gbl.py
# 5/24/2021
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# Global dictionaries

import numpy as np

# Global Dictionary to hold shared TLM values
telemetry = {
    'id': 0,
    'env_temp': 0.0,
    'env_press': 0.0,
    'env_hum': 0.0,
    'sns_temp_1': 0.0,
    'sns_temp_2': 0.0,
    'sns_temp_3': 0.0,
    'sns_temp_4': 0.0,
    'sns_temp_5': 0.0,
    'sns_temp_6': 0.0,
    'sns_temp_7': 0.0,
    'sns_temp_8': 0.0,
    'sns_temp_9': 0.0,
    'sns_temp_10': 0.0,
    'sns_temp_11': 0.0,
    'sns_temp_12': 0.0,
    'sns_units_1': 'K',
    'sns_units_2': 'K',
    'sns_units_3': 'K',
    'sns_units_4': 'K',
    'sns_units_5': 'K',
    'sns_units_6': 'K',
    'sns_units_7': 'K',
    'sns_units_8': 'K',
    'sns_units_9': 'K',
    'sns_units_10': 'K',
    'sns_units_11': 'K',
    'sns_units_12': 'K',
    'dac_fp_1': 0.0,
    'dac_fp_2': 0.0,
    'dac_current_1': 0.0,
    'dac_current_2': 0.0,
    'hipwr_current_1': 0.0,
    'hipwr_current_2': 0.0
}

# Polynomial Coefficients for various sensor calibrations
sensor_cal = {
    'PT100':    [3.12941166e+01, 2.20994204e+00, 3.38698216e-03, -3.74094738e-05,
                7.52012215e-07, -1.10816157e-08, 9.93945028e-11, -5.39794100e-13,
                1.74786835e-15, -3.11421445e-18, 2.35380893e-21],

    'PT1000':   [-8.95535838e+02, 7.29678321e+00, -2.36668702e-02, 4.58446044e-05,
                -5.68116969e-08, 4.71325395e-11, -2.65439231e-14, 1.00329915e-17,
                -2.43888703e-21, 3.44720452e-25, -2.15386906e-29],

    'DIODE':    [3.46854938e+02, 4.57243431e+03, -5.11797585e+04, 2.73214368e+05,
                -8.53948166e+05, 1.65641406e+06, -2.04518237e+06, 1.60463192e+06,
                -7.73031724e+05, 2.08250111e+05, -2.40013209e+04]
}