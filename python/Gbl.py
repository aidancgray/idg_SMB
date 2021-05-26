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
    'rtd0': np.nan,
    'rtd1': np.nan,
    'rtd2': np.nan,
    'rtd3': np.nan,
    'rtd4': np.nan,
    'rtd5': np.nan,
    'rtd6': np.nan,
    'rtd7': np.nan,
    'rtd8': np.nan,
    'rtd9': np.nan,
    'rtd10': np.nan,
    'rtd11': np.nan,
    'rtd12': np.nan,
    'adc_int_temp1': 0.0,
    'adc_int_temp2': 0.0,
    'adc_int_temp3': 0.0,
    'adc_int_temp4': 0.0,
    'adc_int_temp5': 0.0,
    'adc_int_temp6': 0.0,
    'adc_int_temp7': 0.0,
    'adc_int_temp8': 0.0,
    'adc_int_temp9': 0.0,
    'adc_int_temp10': 0.0,
    'adc_int_temp11': 0.0,
    'adc_int_temp12': 0.0,
    'adc_ext_therm1:': 0.0,
    'adc_ext_therm2:': 0.0,
    'adc_ext_therm3:': 0.0,
    'adc_ext_therm4:': 0.0,
    'adc_ext_therm5:': 0.0,
    'adc_ext_therm6:': 0.0,
    'adc_ext_therm7:': 0.0,
    'adc_ext_therm8:': 0.0,
    'adc_ext_therm9:': 0.0,
    'adc_ext_therm10:': 0.0,
    'adc_ext_therm11:': 0.0,
    'adc_ext_therm12:': 0.0,
    'adc_vddio1': 0.0,
    'adc_vddio2': 0.0,
    'adc_vddio3': 0.0,
    'adc_vddio4': 0.0,
    'adc_vddio5': 0.0,
    'adc_vddio6': 0.0,
    'adc_vddio7': 0.0,
    'adc_vddio8': 0.0,
    'adc_vddio9': 0.0,
    'adc_vddio10': 0.0,
    'adc_vddio11': 0.0,
    'adc_vddio12': 0.0,
    'adc_ref_volt1': 0.0,
    'adc_ref_volt2': 0.0,
    'adc_ref_volt3': 0.0,
    'adc_ref_volt4': 0.0,
    'adc_ref_volt5': 0.0,
    'adc_ref_volt6': 0.0,
    'adc_ref_volt7': 0.0,
    'adc_ref_volt8': 0.0,
    'adc_ref_volt9': 0.0,
    'adc_ref_volt10': 0.0,
    'adc_ref_volt11': 0.0,
    'adc_ref_volt12': 0.0,
    'adc_counts1': 0.0,
    'adc_counts2': 0.0,
    'adc_counts3': 0.0,
    'adc_counts4': 0.0,
    'adc_counts5': 0.0,
    'adc_counts6': 0.0,
    'adc_counts7': 0.0,
    'adc_counts8': 0.0,
    'adc_counts9': 0.0,
    'adc_counts10': 0.0,
    'adc_counts11': 0.0,
    'adc_counts12': 0.0,
    'adc_sns_volts1': 0.0,
    'adc_sns_volts2': 0.0,
    'adc_sns_volts3': 0.0,
    'adc_sns_volts4': 0.0,
    'adc_sns_volts5': 0.0,
    'adc_sns_volts6': 0.0,
    'adc_sns_volts7': 0.0,
    'adc_sns_volts8': 0.0,
    'adc_sns_volts9': 0.0,
    'adc_sns_volts10': 0.0,
    'adc_sns_volts11': 0.0,
    'adc_sns_volts12': 0.0,
    'adc_sns_ohms1': 0.0,
    'adc_sns_ohms2': 0.0,
    'adc_sns_ohms3': 0.0,
    'adc_sns_ohms4': 0.0,
    'adc_sns_ohms5': 0.0,
    'adc_sns_ohms6': 0.0,
    'adc_sns_ohms7': 0.0,
    'adc_sns_ohms8': 0.0,
    'adc_sns_ohms9': 0.0,
    'adc_sns_ohms10': 0.0,
    'adc_sns_ohms11': 0.0,
    'adc_sns_ohms12': 0.0,
    'refin1': 0.0,
    'refin2': 0.0,
    'refin3': 0.0,
    'refin4': 0.0,
    'refin5': 0.0,
    'refin6': 0.0,
    'refin7': 0.0,
    'refin8': 0.0,
    'refin9': 0.0,
    'refin10': 0.0,
    'refin11': 0.0,
    'refin12': 0.0,
    'itherm1': 0.0,
    'itherm2': 0.0,
    'itherm3': 0.0,
    'itherm4': 0.0,
    'itherm5': 0.0,
    'itherm6': 0.0,
    'itherm7': 0.0,
    'itherm8': 0.0,
    'itherm9': 0.0,
    'itherm10': 0.0,
    'itherm11': 0.0,
    'itherm12': 0.0,
    'htr_current1': 0.0,
    'htr_current2': 0.0,
}

sensor_cal = {
    1: {
        'coeffs': [],
        'zl': 0,
        'zu': 0
    },
    2: {
        'coeffs': [],
        'zl': 0,
        'zu': 0
    },
    3: {
        'coeffs': [],
        'zl': 0,
        'zu': 0
    },
    4: {
        'coeffs': [],
        'zl': 0,
        'zu': 0
    },
    5: {
        'coeffs': [],
        'zl': 0,
        'zu': 0
    },
    6: {
        'coeffs': [],
        'zl': 0,
        'zu': 0
    },
    7: {
        'coeffs': [],
        'zl': 0,
        'zu': 0
    },
    8: {
        'coeffs': [],
        'zl': 0,
        'zu': 0
    },
    9: {
        'coeffs': [],
        'zl': 0,
        'zu': 0
    },
    10: {
        'coeffs': [],
        'zl': 0,
        'zu': 0
    },
    11: {
        'coeffs': [],
        'zl': 0,
        'zu': 0
    },
    12: {
        'coeffs': [],
        'zl': 0,
        'zu': 0
    }
}