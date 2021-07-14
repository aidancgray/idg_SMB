# CMD_DICT.py
# 5/24/2021
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# Dictionaries for set & get commands

cmd_set_dict = {
        'id': {'P#': 1,
                'P1_MIN': 0,
                'P1_MAX': 255,
                'P2_MIN': None,
                'P2_MAX': None,
                'DESC': 'Store Board ID'},
        'pid_d': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': 0,
                'P2_MAX': 1000000,
                'DESC': 'PID Derivative D Factor'},
        'rst': {'P#': 0,
                'P1_MIN': None,
                'P1_MAX': None,
                'P2_MIN': None,
                'P2_MAX': None,
                'DESC': 'Reset CPU'},
        'hi_pwr': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': 0,
                'P2_MAX': 1,
                'DESC': 'Switched High Power Output'},    
        'pid_i': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': 0,
                'P2_MAX': 1000000,
                'DESC': 'PID Integral I Factor'},
        'lcs': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': 1,
                'P2_MAX': 12,
                'DESC': 'Loop control sensor #'},
        'htr_ena': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': 0,
                'P2_MAX': 2,
                'DESC': '0=Disabled, 1=Fixed%, 2=PID Control'},
        'pid_p': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': 0,
                'P2_MAX': 1000000,
                'DESC': 'PID Proportional P factor'},
        'adc_filt': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 12,
                'P2_MIN': 0,
                'P2_MAX': 4,
                'DESC': 'ADC Filter Setting'},
        'sns_typ': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 12,
                'P2_MIN': 0,
                'P2_MAX': 6,
                'DESC': 'Store Sensor Type (1=PT100, 2=PT1000, 3=NCT_THERMISTOR'},
        'sns_units': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 12,
                'P2_MIN': None,
                'P2_MAX': None,
                'DESC': 'Store Temperature Units'},
        'sns_cal': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 12,
                'P2_MIN': None,
                'P2_MAX': None,
                'DESC': 'Sensor Calibration Data'},
        'sns_cal_coeffs': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 12,
                'P2_MIN': None,
                'P2_MAX': None,
                'DESC': 'Sensor Calibration Coefficients'},
        'htr_cur': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': 0,
                'P2_MAX': 0.1,
                'DESC': 'Set Heater Current (A)'},
        'htr_res': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': 1,
                'P2_MAX': 65536,
                'DESC': 'Set Heater Resistance (Ohms)'},
        'setpoint': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': -460,
                'P2_MAX': 500,
                'DESC': 'Set LOOP SetPoint'},
        'excit': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 12,
                'P2_MIN': 0,
                'P2_MAX': 7,
                'DESC': 'Store Excit uA(0=None, 1=50, 2=100, 3=250, 4=500, 5=750, 6,7=1000'},
        'update_eeprom': {'P#': 0,
                'P1_MIN': None,
                'P1_MAX': None,
                'P2_MIN': None,
                'P2_MAX': None,
                'DESC': 'Store the current configuration in the eeprom for next reboot.'
        } 
}

cmd_get_dict = {
        'id': {'P#': 0,
                'P1_MIN': None,
                'P1_MAX': None,
                'RET_MIN': 0,
                'RET_MAX': 255,
                'DESC': 'Read Board ID'},
        'pid_d': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': 0,
                'RET_MAX': 100,
                'DESC': 'Read PID Derivative D Factor'},
        'hi_pwr': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': 0,
                'RET_MAX': 1,
                'DESC': 'Read Switched High Power Output'},    
        'pid_i': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': 0,
                'RET_MAX': 100,
                'DESC': 'Read PID Integral I Factor'},
        'lcs': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': 1,
                'RET_MAX': 12,
                'DESC': 'Read Loop control sensor #'},
        'sns_temp': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 12,
                'RET_MIN': None,
                'RET_MAX': None,
                'DESC': 'Read Sensor Temperature'},
        'htr_ena': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': 0,
                'RET_MAX': 2,
                'DESC': '0=Disabled, 1=Fixed%, 2=PID Control'},
        'sw_rev': {'P#': 1,
                'P1_MIN': None,
                'P1_MAX': None,
                'RET_MIN': None,
                'RET_MAX': None,
                'DESC': 'Read the Software Revision #'},
        'pid_p': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': 0,
                'RET_MAX': 100,
                'DESC': 'PID Proportional P factor'},
        'adc_filt': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 12,
                'RET_MIN': 0,
                'RET_MAX': 4,
                'DESC': 'ADC Filter Setting'},
        'sns_typ': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 12,
                'RET_MIN': 1,
                'RET_MAX': 6,
                'DESC': 'Store Sensor Type (1=PT100, 2=PT1000, 3=NCT_THERMISTOR'},
        'sns_units': {'P#': 1,
                'P1_MIN': 0,
                'P1_MAX': 4095,
                'RET_MIN': 0,
                'RET_MAX': 2,
                'DESC': 'Read Temperature Units'},
        'sns_cal_coeffs': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 12,
                'RET_MIN': None,
                'RET_MAX': None,
                'DESC': 'Sensor Calibration Coefficients'},
        'htr_cur': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': 0,
                'RET_MAX': 0.1,
                'DESC': 'Get Heater Current (A)'},
        'htr_res': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': None,
                'RET_MAX': None,
                'DESC': 'Get Heater Resistance (Ohms)'},
        'setpoint': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': -460,
                'RET_MAX': 500,
                'DESC': 'Get LOOP SetPoint'},
        'excit': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 12,
                'RET_MIN': 0,
                'RET_MAX': 7,
                'DESC': 'Store Excit uA(0=None, 1=50, 2=100, 3=250, 4=500, 5=750, 6,7=1000'},
        'env': {'P#': 1,
                'P1_MIN': None,
                'P1_MAX': None,
                'RET_MIN': None,
                'RET_MAX': None,
                'DESC': 'Get the environment: temperature, pressure, humidity, or all'},
        'eeprom': {'P#': 0,
                'P1_MIN': None,
                'P1_MAX': None,
                'RET_MIN': None,
                'RET_MAX': None,
                'DESC': 'Printout all of the eeprom memory map to the logger'}
}