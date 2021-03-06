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
        'reset': {'P#': 0,
                'P1_MIN': None,
                'P1_MAX': None,
                'P2_MIN': None,
                'P2_MAX': None,
                'DESC': 'Reset CPU'},
        'update_eeprom': {'P#': 0,
                'P1_MIN': None,
                'P1_MAX': None,
                'P2_MIN': None,
                'P2_MAX': None,
                'DESC': 'Store the current configuration in the eeprom for next reboot.'},
        'stop_program': {'P#': 0,
                'P1_MIN': None,
                'P1_MAX': None,
                'P2_MIN': None,
                'P2_MAX': None,
                'DESC': 'Stop the software from running.'},
        'dac_lcs': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': 0,
                'P2_MAX': 12,
                'DESC': 'Loop control sensor #'},
        'dac_mode': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': 0,
                'P2_MAX': 3,
                'DESC': '0=Disabled, 1=Fixed%, 2=PID Control, 3=Set Current'},
        'dac_res': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': 1,
                'P2_MAX': 65536,
                'DESC': 'Set Heater Resistance (Ohms)'},
        'dac_current': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': 0,
                'P2_MAX': 0.096,
                'DESC': 'Set DAC Heater Current (A)'},
        'dac_fp': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': 0.0,
                'P2_MAX': 1.0,
                'DESC': 'Set Fixed Percent Power (%)'},
        'dac_setpoint': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': -460,
                'P2_MAX': 500,
                'DESC': 'Set LOOP SetPoint'},
        'dac_max_temp': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': -460,
                'P2_MAX': 500,
                'DESC': 'Set Max Temperature Threshold'},
        'dac_min_temp': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': -460,
                'P2_MAX': 500,
                'DESC': 'Set Min Temperature Threshold'},
        'dac_p': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': 0,
                'P2_MAX': 1000000,
                'DESC': 'PID Proportional P factor'},
        'dac_i': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': 0,
                'P2_MAX': 1000000,
                'DESC': 'PID Integral I Factor'},
        'dac_d': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': 0,
                'P2_MAX': 1000000,
                'DESC': 'PID Derivative D Factor'},
        'hipwr_lcs': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': 0,
                'P2_MAX': 12,
                'DESC': 'Set control sensor #'},
        'hipwr_mode': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': 0,
                'P2_MAX': 2,
                'DESC': 'Switched High Power Output'},
        'hipwr_setpoint': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': -460,
                'P2_MAX': 500,
                'DESC': 'Set LOOP SetPoint'},
        'hipwr_state': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': 0,
                'P2_MAX': 1,
                'DESC': '0=Off, 1=On'},
        'hipwr_hysteresis': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': 0,
                'P2_MAX': 100,
                'DESC': 'Set deviation from setpoint for thermostatic control'},
        'hipwr_max_temp': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': -460,
                'P2_MAX': 500,
                'DESC': 'Set Max Temperature Threshold'},
        'hipwr_min_temp': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': -460,
                'P2_MAX': 500,
                'DESC': 'Set Min Temperature Threshold'},
        'sns_type': {'P#': 2,
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
        'reset_adc': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 12,
                'P2_MIN': None,
                'P2_MAX': None,
                'DESC': 'resets the ADC'},
        'adc_filt': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 12,
                'P2_MIN': 0,
                'P2_MAX': 4,
                'DESC': 'ADC Filter Setting'},
        'excit': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 12,
                'P2_MIN': 0,
                'P2_MAX': 7,
                'DESC': 'Store Excit uA(0=None, 1=50, 2=100, 3=250, 4=500, 5=750, 6,7=1000'}
}

cmd_get_dict = {
        'id': {'P#': 0,
                'P1_MIN': None,
                'P1_MAX': None,
                'RET_MIN': 0,
                'RET_MAX': 255,
                'DESC': 'Read Board ID'},
        'sw_rev': {'P#': 1,
                'P1_MIN': None,
                'P1_MAX': None,
                'RET_MIN': None,
                'RET_MAX': None,
                'DESC': 'Read the Software Revision #'},
        'eeprom': {'P#': 0,
                'P1_MIN': None,
                'P1_MAX': None,
                'RET_MIN': None,
                'RET_MAX': None,
                'DESC': 'Printout all of the eeprom memory map to the logger'},
        'dac_lcs': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': 0,
                'RET_MAX': 12,
                'DESC': 'Read Loop control sensor #'},
        'dac_mode': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': 0,
                'RET_MAX': 2,
                'DESC': '0=Disabled, 1=Fixed%, 2=PID Control'},
        'dac_res': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': None,
                'RET_MAX': None,
                'DESC': 'Get Heater Resistance (Ohms)'},
        'dac_current': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': 0,
                'RET_MAX': 0.096,
                'DESC': 'Get DAC Heater Current (A)'},
        'dac_fp': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': 0.0,
                'RET_MAX': 1.0,
                'DESC': 'Get Fixed Percent Power (%)'},
        'dac_setpoint': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': -460,
                'RET_MAX': 500,
                'DESC': 'Get LOOP SetPoint'},
        'dac_max_temp': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': -460,
                'RET_MAX': 500,
                'DESC': 'Get maximum threshold temperature'},
        'dac_min_temp': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': -460,
                'RET_MAX': 500,
                'DESC': 'Get minimum threshold temperature'},
        'dac_p': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': 0,
                'RET_MAX': 100,
                'DESC': 'PID Proportional P factor'},
        'dac_i': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': 0,
                'RET_MAX': 100,
                'DESC': 'Read PID Integral I Factor'},
        'dac_d': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': 0,
                'RET_MAX': 100,
                'DESC': 'Read PID Derivative D Factor'},
        'hipwr_lcs': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': 0,
                'RET_MAX': 12,
                'DESC': 'Read Control Sensor #'},    
        'hipwr_mode': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': 0,
                'RET_MAX': 2,
                'DESC': 'Read Switched High Power Output'},
        'hipwr_setpoint': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': -460,
                'RET_MAX': 500,
                'DESC': 'Get LOOP SetPoint'},
        'hipwr_state': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': 0,
                'RET_MAX': 1,
                'DESC': '0=Off, 1=On'},
        'hipwr_hysteresis': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': 0,
                'RET_MAX': 100,
                'DESC': 'Get deviation from setpoint for thermostatic control'},
        'hipwr_max_temp': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': -460,
                'RET_MAX': 500,
                'DESC': 'Get maximum threshold temperature'},
        'hipwr_min_temp': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': -460,
                'RET_MAX': 500,
                'DESC': 'Get minimum threshold temperature'},
        'hipwr_current': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': 0,
                'RET_MAX': 0.1,
                'DESC': 'Get heater current'},
        'sns_type': {'P#': 1,
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
        'sns_temp': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 12,
                'RET_MIN': None,
                'RET_MAX': None,
                'DESC': 'Read Sensor Temperature'},
        'sns_res': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 12,
                'RET_MIN': None,
                'RET_MAX': None,
                'DESC': 'Read Sensor Resistance'},
        'sns_volts': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 12,
                'RET_MIN': None,
                'RET_MAX': None,
                'DESC': 'Read Sensor Voltage'},
        'adc_filt': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 12,
                'RET_MIN': 0,
                'RET_MAX': 4,
                'DESC': 'ADC Filter Setting'},
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
                'DESC': 'Get the environment: temperature, pressure, humidity, or all'}
}