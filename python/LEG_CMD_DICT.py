leg_action_dict = {
    'A': {  'P1_MIN': 0,
            'P1_MAX': 255,
            'P2_MIN': None,
            'P2_MAX': None,
            'DESC': 'Store Board ID'},
    'D': {  'P1_MIN': 1,
            'P1_MAX': 2,
            'P2_MIN': None,
            'P2_MAX': None,
            'DESC': 'PID Derivative D Factor'},
    'E': {  'P1_MIN': None,
            'P1_MAX': None,
            'P2_MIN': None,
            'P2_MAX': None,
            'DESC': 'Reset CPU'},
    'F': {  'P1_MIN': 1,
            'P1_MAX': 2,
            'P2_MIN': 0,
            'P2_MAX': 1,
            'DESC': 'Switched High Power Output'},    
    'I': {  'P1_MIN': 1,
            'P1_MAX': 2,
            'P2_MIN': 0,
            'P2_MAX': 100,
            'DESC': 'PID Integral I Factor'},
    'J': {  'P1_MIN': 1,
            'P1_MAX': 2,
            'P2_MIN': 1,
            'P2_MAX': 12,
            'DESC': 'Loop control sensor #'},
    'L': {  'P1_MIN': 1,
            'P1_MAX': 2,
            'P2_MIN': 0,
            'P2_MAX': 2,
            'DESC': '0=Disabled, 1=Fixed%, 2=PID Control'},
    'P': {  'P1_MIN': 1,
            'P1_MAX': 2,
            'P2_MIN': 0,
            'P2_MAX': 100,
            'DESC': 'PID Proportional P factor'},
    'Q': {  'P1_MIN': 1,
            'P1_MAX': 12,
            'P2_MIN': 0,
            'P2_MAX': 4,
            'DESC': 'ADC Filter Setting'},
    'S': {  'P1_MIN': 1,
            'P1_MAX': 12,
            'P2_MIN': None,
            'P2_MAX': None,
            'DESC': 'Store Sensor Type (1=PT100, 2=PT1000, 3=NCT_THERMISTOR'},
    'U': {  'P1_MIN': 0,
            'P1_MAX': 4095,
            'P2_MIN': 0,
            'P2_MAX': 2,
            'DESC': 'Store Temperature Units'},
    'V': {  'P1_MIN': 1,
            'P1_MAX': 2,
            'P2_MIN': 0,
            'P2_MAX': 0.1,
            'DESC': 'Set Heature Current (A)'},
    'W': {  'P1_MIN': 1,
            'P1_MAX': 2,
            'P2_MIN': -460,
            'P2_MAX': 500,
            'DESC': 'Set LOOP SetPoint'},
    'X': {  'P1_MIN': 1,
            'P1_MAX': 12,
            'P2_MIN': 0,
            'P2_MAX': 7,
            'DESC': 'Store Excit uA(0=None, 1=50, 2=100, 3=250, 4=500, 5=750, 6,7=1000'}
}

leg_query_dict = {
    'A': {  'P1_MIN': 0,
            'P1_MAX': 255,
            'RET_MIN': None,
            'RET_MAX': None,
            'DESC': 'Read Board ID'},
    'D': {  'P1_MIN': 1,
            'P1_MAX': 2,
            'RET_MIN': 0,
            'RET_MAX': 100,
            'DESC': 'Read PID Derivative D factor'},
    'F': {  'P1_MIN': 1,
            'P1_MAX': 2,
            'RET_MIN': 0,
            'RET_MAX': 1,
            'DESC': 'Read Switched High Power Output'},
    'H': {  'P1_MIN': None,
            'P1_MAX': None,
            'RET_MIN': 0,
            'RET_MAX': 100,
            'DESC': 'Read Humidity Sensor'},
    'I': {  'P1_MIN': 1,
            'P1_MAX': 2,
            'RET_MIN': 0,
            'RET_MAX': 100,
            'DESC': 'Read PID Integral I Factor'},
    'J': {  'P1_MIN': 1,
            'P1_MAX': 2,
            'RET_MIN': 1,
            'RET_MAX': 12,
            'DESC': 'Read Loop Control Sensor'},
    'K': {  'P1_MIN': 1,
            'P1_MAX': 12,
            'RET_MIN': None,
            'RET_MAX': None,
            'DESC': 'Read Sensor Temperature'},
    'L': {  'P1_MIN': 1,
            'P1_MAX': 2,
            'RET_MIN': 0,
            'RET_MAX': 2,
            'DESC': 'Read Htr Amp'},
    'N': {  'P1_MIN': None,
            'P1_MAX': None,
            'RET_MIN': None,
            'RET_MAX': None,
            'DESC': 'Read the software revision'},
    'P': {  'P1_MIN': 1,
            'P1_MAX': 2,
            'RET_MIN': 0,
            'RET_MAX': 100,
            'DESC': 'Read PID Proportional P Factor'},
    'Q': {  'P1_MIN': 1,
            'P1_MAX': 12,
            'RET_MIN': 0,
            'RET_MAX': 4,
            'DESC': 'Read Filter Setting'},
    'S': {  'P1_MIN': 1,
            'P1_MAX': 12,
            'RET_MIN': 0,
            'RET_MAX': 3,
            'DESC': 'Read SensorType (1=PT100, 2=PT1000, 3=NCT_THERMISTOR'},
    'U': {  'P1_MIN': 1,
            'P1_MAX': 12,
            'RET_MIN': 0,
            'RET_MAX': 2,
            'DESC': 'Read Temperature Units (0=K, 1=C, 2=F'},
    'V': {  'P1_MIN': 1,
            'P1_MAX': 2,
            'RET_MIN': 0,
            'RET_MAX': 0.1,
            'DESC': 'Read Heater Current (A)'},
    'W': {  'P1_MIN': 1,
            'P1_MAX': 2,
            'RET_MIN': -460,
            'RET_MAX': 500,
            'DESC': 'Read LOOP SetPoint'},
    'X': {  'P1_MIN': 1,
            'P1_MAX': 12,
            'RET_MIN': 0,
            'RET_MAX': 7,
            'DESC': 'Read Excit uA(0=None, 1=50, 2=100, 3=250, 4=500, 5=750, 6,7=1000'},
    'd': {  'P1_MIN': None,
            'P1_MAX': None,
            'RET_MIN': None,
            'RET_MAX': None,
            'DESC': 'Read RTD raw ADC values'},
    'r': {  'P1_MIN': None,
            'P1_MAX': None,
            'RET_MIN': None,
            'RET_MAX': None,
            'DESC': 'Read RTD resistance at temperature'},
    'v': {  'P1_MIN': None,
            'P1_MAX': None,
            'RET_MIN': None,
            'RET_MAX': None,
            'DESC': 'Read RTD voltage at temperature'},
    't': {  'P1_MIN': None,
            'P1_MAX': None,
            'RET_MIN': None,
            'RET_MAX': None,
            'DESC': 'Read temperatures from all channels'},
}