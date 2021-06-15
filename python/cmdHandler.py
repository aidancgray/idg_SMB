# cmdHandler.py
# 5/24/2021
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# Command Handler loop. Runs in parallel with the TCP Server and
# Transmit loops. It constantly monitors the Command Queue and 
# acts upon new commands in the order they are received. It also
# populates the Telemetry dictionary.

import logging
import asyncio
import time
from CMD_DICT import cmd_set_dict, cmd_get_dict
from LEG_CMD_DICT import leg_action_dict, leg_query_dict
from chebyFit import chebyFit

class CMDLoop:
    def __init__(self, qCmd, qXmit, eeprom, tlm, cal, io, bme280, ads1015, hi_pwr_htrs, dacList, adcList):
        self.logger = logging.getLogger('smb')
        self.qCmd = qCmd
        self.qXmit = qXmit
        self.eeprom = eeprom
        self.tlm = tlm
        self.cal = cal
        self.io = io
        self.bme280 = bme280
        self.ads1015 = ads1015
        self.hi_pwr_htrs = hi_pwr_htrs
        self.dacList = dacList
        self.adcList = adcList

    async def start(self):
        lastTime = 0
        while True:
            newTime = time.perf_counter()
            if lastTime == 0:
                tempTime = newTime - 1

            ### Get BME280 environment data ###
            self.tlm['env_temp'] = self.bme280.get_temperature()
            self.tlm['env_press'] = self.bme280.get_pressure()
            self.tlm['env_hum'] = self.bme280.get_humidity()

            ### Heater Loop ###
            # check if a conversion is occurring
            if self.ads1015.conversion_status() == 1:
                lastConvert = self.ads1015.last_convert()
                lastCurrent = self.ads1015.conversion_read()
                
                # check which conversion happened last
                if lastConvert == 0:
                    self.tlm['htr_current1'] = lastCurrent
                    self.ads1015.convert_3()

                elif lastConvert == 3:
                    self.tlm['htr_current2'] = lastCurrent
                    self.ads1015.convert_0()

            ### Temperature Sensor ###
            # TODO: 
            # + get sensor readings 
            # - convert readings using chebyFits
            # + update telemetry
            # - update PID loops in each DAC from dacList
            
            # Update temperature values every 1 second
            if newTime - tempTime >= 1:
                for n in range(len(self.adcList)):
                    temp = self.adcList[n].get_DATA()

                    # Convert Reading


                    self.tlm['adc_int_temp'+str(n+1)] = temp
                tempTime = time.perf_counter()


            ### Check the Command Queue ###
            if not self.qCmd.empty():
                msg = await self.qCmd.get()
                writer = msg[0]
                cmd = msg[1]
                retData = await self.parse_raw_command(cmd)
                await self.enqueue_xmit((writer, retData+'\n'))

            lastTime = newTime
            await asyncio.sleep(0.000001)

    async def parse_raw_command(self, rawCmd):
        cmdStr = rawCmd.strip()  # remove whitespace at the end
        
        if cmdStr[0] == '~' or cmdStr[0] == '?':
            retData = await self.legacy_command_parser(cmdStr)
        
        elif cmdStr[0] == '$':
            cmdStr = cmdStr[1:]  # Remove the start character
            # cmdStr = cmdStr.replace(' ', '')  # Remove all whitespace
            cmdStrList = cmdStr.split(',')  # split the command on the commas
            
            if cmdStrList[0] == 'set':
                retData = await self.parse_set_command(cmdStrList[1:])

            elif cmdStrList[0] == 'get':
                retData = await self.parse_get_command(cmdStrList[1:])

            else:
                retData = 'BAD,command failure: second arg must be \'set\' or \'get\''
                self.logger.error(retData)

        else:
            retData = 'BAD,command failure: must start with \'~\', \'?\', or \'$\''
            self.logger.error(retData)

        if 'BAD' not in retData and 'OK' not in retData:
            retData = 'OK,'+retData

        return retData

    async def parse_set_command(self, cmdStr):
        if cmdStr[0] in cmd_set_dict:
            cmd_dict = cmd_set_dict[cmdStr[0]]

            # Check if cmd parameters meet cmd_dict requirements
            if cmd_dict['P#'] == 0:
                if len(cmdStr) == 1:
                    retData = await self.execute_set_command(cmd_dict, cmdStr[0], [None, None])
                    
                else:
                    retData = 'BAD,command failure: This command accepts no args'
                    self.logger.error(retData)

            elif cmd_dict['P#'] == 1:
                if len(cmdStr) == 2:
                    retData = await self.execute_set_command(cmd_dict, cmdStr[0], [cmdStr[1], None])

                else:
                    retData = 'BAD,command failure: This command requires 1 arg'
                    self.logger.error(retData)

            elif cmd_dict['P#'] == 2:
                if len(cmdStr) == 3:
                    retData = await self.execute_set_command(cmd_dict, cmdStr[0], cmdStr[1:3])

                else:
                    retData = 'BAD,command failure: This command requires 2 args'
                    self.logger.error(retData)
            else:
                    retData = 'BAD,command dictionary failure: Command requires too many args'
                    self.logger.error(retData)
        else:
            retData = 'BAD,command failure: cmd arg invalid'
            self.logger.error(retData)
        
        return retData

    async def parse_get_command(self, cmdStr):
        if cmdStr[0] in cmd_get_dict:
            cmd_dict = cmd_get_dict[cmdStr[0]]
            
            # Check if cmd parameters meet cmd_dict requirements
            if cmd_dict['P#'] == 0:
                if len(cmdStr) == 1:
                    retData = await self.execute_get_command(cmd_dict, cmdStr[0], [None])

                else:
                    retData = 'BAD,command failure: This command accepts no args'
                    self.logger.error(retData)

            elif cmd_dict['P#'] == 1:
                if len(cmdStr) == 2:
                    retData = await self.execute_get_command(cmd_dict, cmdStr[0], cmdStr[1:2])

                else:
                    retData = 'BAD,command failure: This command requires 1 arg'
                    self.logger.error(retData)

            else:
                    retData = 'BAD,command dictionary failure: Command requires too many args'
                    self.logger.error(retData)

        else:
            retData = 'BAD,command failure: cmd arg invalid'
            self.logger.error(retData)

        return retData

    async def execute_set_command(self, cmd_dict, cmd, params):
        p1 = params[0]
        p2 = params[1]
        pnum = cmd_dict['P#']
        p1min = cmd_dict['P1_MIN']
        p1max = cmd_dict['P1_MAX']
        p2min = cmd_dict['P2_MIN']
        p2max = cmd_dict['P2_MAX']
        output = 'OK'

        try:
            # Check p1
            if p1min == None and p1max == None:
                pass
            elif p1min == None and float(p1) <= p1max:
                p1 = float(p1)
            elif p1max == None and float(p1) >= p1min:
                p1 = float(p1)
            elif float(p1) >= p1min and float(p1) <= p1max:
                p1 = float(p1)
            else:
                retData = 'BAD,command failure: arg 1 out of range'
                self.logger.error(retData)
                return retData

            # Check p2
            if p2min == None and p2max == None:
                pass
            elif p2min == None and float(p2) <= p2max:
                p2 = float(p2)
            elif p2max == None and float(p2) >= p2min:
                p2 = float(p2)
            elif float(p2) >= p2min and float(p2) <= p2max:
                p2 = float(p2)
            else:
                retData = 'BAD,command failure: arg 2 out of range'
                self.logger.error(retData)
                return retData

            # Handle each command case
            
            if cmd == 'id':
                self.tlm['id'] = p1
                retData = 'OK'
            
            elif cmd == 'pid_d':
                intP1 = int(p1 - 1)
                self.dacList[intP1].kd = p2
                retData = 'OK'

            elif cmd == 'rst':
                pass

            elif cmd == 'hi_pwr':
                if int(p2) == 0:
                    self.hi_pwr_htrs[int(p1)-1].power_off()
                elif int(p2) == 1:
                    self.hi_pwr_htrs[int(p1)-1].power_on()
                retData = 'OK'

            elif cmd == 'pid_i':
                intP1 = int(p1 - 1)
                self.dacList[intP1].ki = p2
                retData = 'OK'

            elif cmd == 'lcs':
                pass

            elif cmd == 'htr_ena':
                pass

            elif cmd == 'pid_p':
                intP1 = int(p1 - 1)
                self.dacList[intP1].kp = p2
                retData = 'OK'

            elif cmd == 'adc_filt':
                pass

            elif cmd == 'sns_typ':
                sns = int(p1 - 1)
                self.adcList[sns].sns_typ = p2
                retData = 'OK'

            elif cmd == 'sns_units':
                sns = int(p1 - 1)
                self.adcList[sns].sns_units = p2
                retData = 'OK'
            
            elif cmd == 'sns_cal':
                sensor = p1
                tmpCalData = p2.split(';')
                calData = []

                for point in tmpCalData:
                    newPt = point.split(' ')
                    newPt[0] = float(newPt[0])
                    newPt[1] = float(newPt[1])
                    calData.append(newPt)

                # TODO: convert calData[][0] points from sensor units to bits
                chebyshevFit = chebyFit(calData, 10)
                
                self.adcList[p1-1].calib_fit = chebyshevFit  # add the calibration to the ADC

                # Store the calibration info in the global dict (possibly redundant...)
                self.cal[sensor]['coeffs'] = chebyshevFit.chebyFit[0]
                self.cal[sensor]['zl'] = chebyshevFit.chebyFit[1]
                self.cal[sensor]['zu'] = chebyshevFit.chebyFit[2]
                retData = 'OK'

            elif cmd == 'htr_cur':
                pass

            elif cmd == 'setpoint':
                intP1 = int(p1 - 1)
                self.dacList[intP1].setPoint = p2
                retData = 'OK'

            elif cmd == 'excit':
                intP1 = int(p1 - 1)
                self.adcList[intP1].set_excitation_current(p2)
                retData = 'OK'

            else:
                retData = f'BAD,command failure: unknown command {cmd!r}'
                self.logger.error(retData)
                return retData

            return retData
        
        except (TypeError, ValueError):
            retData = 'BAD,command failure: expected args float or int'
            self.logger.error(retData)
            return retData
        
    async def execute_get_command(self, cmd_dict, cmd, params):
        p1 = params[0]
        pnum = cmd_dict['P#']
        p1min = cmd_dict['P1_MIN']
        p1max = cmd_dict['P1_MAX']
        retmin = cmd_dict['RET_MIN']
        retmax = cmd_dict['RET_MAX']

        try:
            # Check p1
            if p1min == None and p1max == None:
                pass
            elif p1min == None and float(p1) <= p1max:
                p1 = float(p1)
            elif p1max == None and float(p1) >= p1min:
                p1 = float(p1)
            elif float(p1) >= p1min and float(p1) <= p1max:
                p1 = float(p1)
            else:
                retData = 'BAD,command failure: args out of range'
                self.logger.error(retData)
                return retData

            # Handle each command case
            
            if cmd == 'id':
                board_id = self.tlm['id']
                retData = f'id={board_id!r}'
            
            elif cmd == 'pid_d':
                intP1 = int(p1 - 1)
                pid_d = self.dacList[intP1].kd
                retData = f'pid_d={pid_d!r}'

            elif cmd == 'hi_pwr':
                retData = self.hi_pwr_htrs[int(p1)-1].status()

                if retData == 0:
                    retData = 'off'
                elif retData == 1:
                    retData = 'on'
                else:
                    retData = 'BAD,GPIO read error'

            elif cmd == 'pid_i':
                intP1 = int(p1 - 1)
                pid_i = self.dacList[intP1].ki
                retData = f'pid_i={pid_i!r}'

            elif cmd == 'lcs':
                pass

            elif cmd == 'sns_temp':
                sensor = str(p1)
                sensor = sensor.split('.')[0]
                sensorName = 'adc_int_temp'+sensor
                temp = self.tlm[sensorName]
                retData = f'sns_temp_{sensor}={temp!r}'

            elif cmd == 'htr_ena':
                pass
            
            elif cmd == 'sw_rev':
                pass

            elif cmd == 'pid_p':
                intP1 = int(p1 - 1)
                pid_p = self.dacList[intP1].kp
                retData = f'pid_p={pid_p!r}'

            elif cmd == 'adc_filt':
                pass

            elif cmd == 'sns_typ':
                sns = int(p1 - 1)
                sns_typ = self.adcList[sns].sns_typ
                retData = f'sns_typ_{sns}={sns_typ}'

            elif cmd == 'sns_units':
                sns = int(p1 - 1)
                sns_units = self.adcList[sns].sns_units
                retData = f'sns_units_{sns}={sns_units}'

            elif cmd == 'htr_cur':
                if p1 == 1:
                    retData = 'htr_cur_1='+str(self.tlm['htr_current1'])
                elif p1 == 2:
                    retData = 'htr_cur_2='+str(self.tlm['htr_current2'])
                else:
                    retData = f'BAD,command failure: unknown arg {p1!r}'

            elif cmd == 'setpoint':
                intP1 = int(p1 - 1)
                setpoint = self.dacList[intP1].setPoint
                retData = f'setpoint={setpoint!r}'

            elif cmd == 'excit':
                intP1 = int(p1 - 1)
                retData = f'excit={self.adcList[intP1].get_excitation_current()}'
            
            # Get BME280 data
            elif cmd == 'env':
                if p1 == 'temp':
                    retData = 'temp='+str(self.tlm['env_temp'])+'C'
                elif p1 == 'press':
                    retData = 'press='+str(self.tlm['env_press'])+'Pa'
                elif p1 == 'hum':
                    retData = 'hum='+str(self.tlm['env_hum'])+'%'
                elif p1 == 'all':
                    retData = 'temp='+str(self.tlm['env_temp'])+'C,press='+str(self.tlm['env_press'])+'Pa,hum='+str(self.tlm['env_hum'])+'%'
                else:
                    retData = f'BAD,command failure: unknown arg {p1!r}'

            else:
                retData = f'BAD,command failure: unknown command {cmd!r}'
                self.logger.error(retData)
                return retData

            return retData

        except TypeError as e1:
            print(e1)
            retData = 'BAD,command failure: expected args float or int'
            self.logger.error(retData)
            return retData

    async def legacy_command_parser(self, cmdStr):
        retData = 'legacy_command_parser is not complete'
        return retData

    async def enqueue_xmit(self, msg):
        await self.qXmit.put(msg)