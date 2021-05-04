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
                'P2_MAX': 100,
                'DESC': 'PID Derivative D Factor'},
        'rst': {'P#': 0,
                'P1_MIN': None,
                'P1_MAX': None,
                'P2_MIN': None,
                'P2_MAX': None,
                'DESC': 'Reset CPU'},
        'bb': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': 0,
                'P2_MAX': 1,
                'DESC': 'Switched High Power Output'},    
        'pid_i': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': 0,
                'P2_MAX': 100,
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
                'P2_MAX': 100,
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
                'P2_MIN': None,
                'P2_MAX': None,
                'DESC': 'Store Sensor Type (1=PT100, 2=PT1000, 3=NCT_THERMISTOR'},
        'sns_units': {'P#': 2,
                'P1_MIN': 0,
                'P1_MAX': 4095,
                'P2_MIN': 0,
                'P2_MAX': 2,
                'DESC': 'Store Temperature Units'},
        'htr_cur': {'P#': 2,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'P2_MIN': 0,
                'P2_MAX': 0.1,
                'DESC': 'Set Heature Current (A)'},
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
        
        'test_a': {'P#': 2,
                'P1_MIN': None,
                'P1_MAX': None,
                'P2_MIN': None,
                'P2_MAX': None,
                'DESC': 'Returns the given strings with \'#\' around the first and \'@\' around the second'},

        'test_b': {'P#': 2,
                'P1_MIN': 0,
                'P1_MAX': 1,
                'P2_MIN': 1,
                'P2_MAX': 12,
                'DESC': 'Checks that the args are between min and max'}        
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
        'bb': {'P#': 1,
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
                'RET_MAX': 3,
                'DESC': 'Store Sensor Type (1=PT100, 2=PT1000, 3=NCT_THERMISTOR'},
        'sns_units': {'P#': 1,
                'P1_MIN': 0,
                'P1_MAX': 4095,
                'RET_MIN': 0,
                'RET_MAX': 2,
                'DESC': 'Read Temperature Units'},
        'htr_cur': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': 0,
                'RET_MAX': 0.1,
                'DESC': 'Set Heature Current (A)'},
        'setpoint': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 2,
                'RET_MIN': -460,
                'RET_MAX': 500,
                'DESC': 'Set LOOP SetPoint'},
        'excit': {'P#': 1,
                'P1_MIN': 1,
                'P1_MAX': 12,
                'RET_MIN': 0,
                'RET_MAX': 7,
                'DESC': 'Store Excit uA(0=None, 1=50, 2=100, 3=250, 4=500, 5=750, 6,7=1000'},

        'test_a': {'P#': 1,
                'P1_MIN': None,
                'P1_MAX': None,
                'RET_MIN': None,
                'RET_MAX': None,
                'DESC': 'Returns the given string with \'#\' around it'},
        
        'test_b': {'P#': 1,
                'P1_MIN': 0,
                'P1_MAX': 1,
                'RET_MIN': None,
                'RET_MAX': None,
                'DESC': 'Checks that the arg is between min and max'}
}