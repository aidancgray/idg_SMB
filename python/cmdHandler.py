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
import queue
import sys
from datetime import datetime
from CMD_DICT import cmd_set_dict, cmd_get_dict
from LEG_CMD_DICT import leg_action_dict, leg_query_dict

class CMDLoop:
    def __init__(self, qCmd, qXmit, eeprom, tlm, cal, io, bme280, ads1015, hi_pwr_htrs, dacList, adcList):
        self.logger = logging.getLogger('smb')
        self.qCmd = qCmd
        self.qXmit = qXmit
        self.qUDP = queue.Queue()
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
            # Update temperature values every 1 second
            if newTime - tempTime >= 1:
                now = datetime.now()

                for n in range(len(self.adcList)):
                    temp = round(self.adcList[n].get_temperature(), 3)
                    # if temp == -999:
                    #     temp = '---'
                    
                    sns_unitsTmp = self.adcList[n].sns_units

                    if sns_unitsTmp == 0:
                        sns_units = 'K'
                    elif sns_unitsTmp == 1:
                        sns_units = 'C'
                    elif sns_unitsTmp == 2:
                        sns_units = 'F'
                    else:
                        raise ValueError(f"Unknown Sensor Units:{sns_unitsTmp} 0=K, 1=C, 2=F")
                    
                    m = f'{n+1:02d}'
                    self.enqueue_udp(f'{now}, temp_{m}={temp}{sns_units}')
                    self.tlm['sns_temp_'+str(n+1)] = temp
                
                # Update DAC Heaters
                for dac in self.dacList:
                    # Ensure mode and sensor number are specified
                    if dac.sns_num != 0 and dac.mode != 0 and dac.htr_res != 0:
                        temp = self.tlm['sns_temp_'+str(dac.sns_num)]
                        sns_unitsTmp = self.adcList[dac.sns_num-1].get_sns_units()
                        if sns_unitsTmp == 0:
                            sns_units = 'K'
                        elif sns_unitsTmp == 1:
                            sns_units = 'C'
                        elif sns_unitsTmp == 2:
                            sns_units = 'F'
                        else:
                            raise ValueError(f"Unknown Sensor Units:{sns_unitsTmp} 0=K, 1=C, 2=F")

                        setpoint = dac.setPoint
                        try:
                            power = round(self.tlm[f'dac_power_{dac.idx+1}'], 5)
                            current = round(self.tlm[f'dac_current_{dac.idx+1}'], 5)

                        except Exception as e:
                            print(f'error: {e}')
                            power = 0
                            current = 0
                        
                        self.enqueue_udp(f'{now}, DAC_{dac.idx}: temp={temp}{sns_units}, setpoint={setpoint}{sns_units}, power={power}, current={current}')
                        
                        if temp < dac.max_temp and temp > dac.min_temp:
                            if dac.mode == 1:
                                dac.fp_update()
                            elif dac.mode == 2:
                                dac.dac_update(temp, sns_unitsTmp)
                            elif dac.mode == 3:
                                dac.set_current_update()
                        else:
                            dac.controlVar = 0.0

                # Update Hi-Power Heaters
                for htr in self.hi_pwr_htrs:
                    if htr.sns_num != 0 and htr.mode != 0:
                        temp = self.tlm['sns_temp_'+str(htr.sns_num)]
                        units = self.adcList[htr.sns_num-1].get_sns_units()
                        self.logger.info(f'HIPWR_{htr.idx}: temp={temp}, units={units}')
                        
                        if temp < htr.max_temp and temp > htr.min_temp:
                            if htr.mode == 2:
                                htr.update_htr(temp, units)
                        else:
                            htr.power_off()

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
        
        if len(cmdStr) != 0:
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
            
            elif cmd == 'reset':
                self.eeprom.reset_eeprom()
                retData = 'OK, please restart Sensor Monitor Board.'
            
            elif cmd == 'update_eeprom':
                for dac in self.dacList:
                    dac.update_eeprom_mem()
                
                for adc in self.adcList:
                    adc.update_eeprom_mem()

                self.ads1015.update_eeprom_mem()
                self.bme280.update_eeprom_mem()

                for htr in self.hi_pwr_htrs:
                    htr.update_eeprom_mem()

                # for htr in self.pid_htrs:
                #     htr.update_eeprom_mem()x
                
                self.eeprom.fill_eeprom()
                retData = 'OK'
            
            elif cmd == 'stop_program':
                # Turn off all DACs
                for dac in self.dacList:
                    dac.write_control_var(0)

                # Turn off all hi-power heaters
                for htr in self.hi_pwr_htrs:
                    htr.power_off()

                sys.exit()

            elif cmd == 'dac_lcs':
                intP1 = int(p1 - 1)
                self.dacList[intP1].sns_num = int(p2)
                retData = 'OK'

            elif cmd == 'dac_mode':
                intP1 = int(p1 - 1)
                self.dacList[intP1].mode = int(p2)
                retData = 'OK'
            
            elif cmd == 'dac_res':
                intP1 = int(p1 - 1)
                self.dacList[intP1].htr_res = p2
                retData = 'OK'

            elif cmd == 'dac_cur':
                intP1 = int(p1 - 1)
                self.dacList[intP1].controlVar = float(p2)
                retData = 'OK'
            
            elif cmd == 'dac_fp':
                intP1 = int(p1 - 1)
                self.dacList[intP1].fixed_percent = float(p2)
                retData = 'OK'

            elif cmd == 'dac_setpoint':
                intP1 = int(p1 - 1)
                self.dacList[intP1].setPoint = float(p2)
                retData = 'OK'

            elif cmd == 'dac_max_temp':
                intP1 = int(p1 - 1)
                self.dacList[intP1].max_temp = float(p2)
                retData = 'OK'
            
            elif cmd == 'dac_min_temp':
                intP1 = int(p1 - 1)
                self.dacList[intP1].min_temp = float(p2)
                retData = 'OK'

            elif cmd == 'dac_p':
                intP1 = int(p1 - 1)
                self.dacList[intP1].kp = p2
                retData = 'OK'
            
            elif cmd == 'dac_i':
                intP1 = int(p1 - 1)
                self.dacList[intP1].ki = p2
                retData = 'OK'

            elif cmd == 'dac_d':
                intP1 = int(p1 - 1)
                self.dacList[intP1].kd = p2
                retData = 'OK'

            elif cmd == 'hipwr_lcs':
                self.hi_pwr_htrs[int(p1)-1].sns_num = int(p2)
                retData = 'OK'

            elif cmd == 'hipwr_mode':
                self.hi_pwr_htrs[int(p1)-1].mode = int(p2)
                retData = 'OK'

            elif cmd == 'hipwr_setpoint':
                intP1 = int(p1 - 1)
                self.hi_pwr_hts[intP1].setPoint = float(p2)
                retData = 'OK'

            elif cmd == 'hipwr_state':
                if int(p2) == 0:
                    self.hi_pwr_htrs[int(p1)-1].power_off()
                    retData = 'OK'
                elif int(p2) == 1:
                    self.hi_pwr_htrs[int(p1)-1].power_on()
                    retData = 'OK'
                else: retData = 'BAD, must be 0 or 1'

            elif cmd == 'hipwr_hysteresis':
                intP1 = int(p1 - 1)
                self.hi_pwr_hts[intP1].hysteresis = float(p2)
                retData = 'OK'

            elif cmd == 'hipwr_max_temp':
                intP1 = int(p1 - 1)
                self.hi_pwr_htrs[intP1].max_temp = float(p2)
                retData = 'OK'
            
            elif cmd == 'hipwr_min_temp':
                intP1 = int(p1 - 1)
                self.hi_pwr_htrs[intP1].min_temp = float(p2)
                retData = 'OK'

            elif cmd == 'sns_type':
                sns = int(p1 - 1)
                sns_type = int(p2)
                self.adcList[sns].set_sns_type(sns_type)
                retData = 'OK'

            elif cmd == 'sns_units':
                retData = 'OK'
                sns = int(p1 - 1)
                if p2 == 'K':
                    units = 0
                    self.adcList[sns].set_sns_units(units)
                elif p2 == 'C':
                    units = 1
                    self.adcList[sns].set_sns_units(units)
                elif p2 == 'F':
                    units = 2
                    self.adcList[sns].set_sns_units(units)
                else:
                    retData = 'BAD: Units must be K, C, F.'
            
            elif cmd == 'sns_cal':
                sns = int(p1 - 1)
                tmpCalData = p2.split(';')
                calData = []

                for point in tmpCalData:
                    newPt = point.split(' ')
                    newPt[0] = float(newPt[0])
                    newPt[1] = float(newPt[1])
                    calData.append(newPt)

                self.adcList[sns].set_calibration(calData)
                retData = 'OK'

            elif cmd == 'sns_cal_coeffs':
                sns = int(p1 - 1)
                calCoeffs = p2.split(';')
                retData = self.adcList[sns].set_calibration_coeffs(calCoeffs)

            elif cmd == 'adc_filt':
                pass
            
            elif cmd == 'excit':
                intP1 = int(p1 - 1)
                self.adcList[intP1].set_excitation_current(p2)
                retData = 'OK'
                
            else:
                retData = f'BAD,command failure: unknown command {cmd!r}'
                self.logger.error(retData)
                return retData

            return retData
        
        except (TypeError, ValueError) as e:
            retData = f'BAD,command failure: expected args float or int = {e}'
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
            
            elif cmd == 'sw_rev':
                pass

            elif cmd == 'eeprom':
                self.eeprom.printout_eeprom()
                retData = 'printing eeprom memory map to logger.'

            elif cmd == 'dac_lcs':
                intP1 = int(p1 - 1)
                sns_num = self.dacList[intP1].sns_num
                retData = f'dac_lcs_{int(p1)}={sns_num!r}'

            elif cmd == 'dac_mode':
                intP1 = int(p1 - 1)
                mode = self.dacList[intP1].mode
                retData = f'dac_mode_{int(p1)}={mode!r}'

            elif cmd == 'dac_res':
                intP1 = int(p1 - 1)
                dac_res = self.dacList[intP1].htr_res
                retData = f'dac_res_{int(p1)}={dac_res!r}'

            elif cmd == 'dac_cur':
                if p1 == 1:
                    retData = 'dac_current_1='+str(self.tlm['dac_current_1'])
                elif p1 == 2:
                    retData = 'dac_current_2='+str(self.tlm['dac_current_2'])
                else:
                    retData = f'BAD,command failure: unknown arg {p1!r}'

            elif cmd == 'dac_fp':
                if p1 == 1:
                    retData = 'dac_fp_1='+str(self.tlm['dac_fp_1'])
                elif p1 == 2:
                    retData = 'dac_fp_2='+str(self.tlm['dac_fp_2'])
                else:
                    retData = f'BAD,command failure: unknown arg {p1!r}'

            elif cmd == 'dac_setpoint':
                intP1 = int(p1 - 1)
                setpoint = self.dacList[intP1].setPoint
                retData = f'dac_setpoint_{int(p1)}={setpoint!r}'

            elif cmd == 'dac_max_temp':
                intP1 = int(p1 - 1)
                dac_max_temp = self.dacList[intP1].max_temp
                retData = f'dac_max_temp_{int(p1)}={dac_max_temp!r}'
            
            elif cmd == 'dac_min_temp':
                intP1 = int(p1 - 1)
                dac_min_temp = self.dacList[intP1].min_temp
                retData = f'dac_min_temp_{int(p1)}={dac_min_temp!r}'

            elif cmd == 'dac_p':
                intP1 = int(p1 - 1)
                pid_p = self.dacList[intP1].kp
                retData = f'pid_p_{int(p1)}={pid_p!r}'

            elif cmd == 'dac_i':
                intP1 = int(p1 - 1)
                pid_i = self.dacList[intP1].ki
                retData = f'pid_i_{int(p1)}={pid_i!r}'

            elif cmd == 'dac_d':
                intP1 = int(p1 - 1)
                pid_d = self.dacList[intP1].kd
                retData = f'pid_d_{int(p1)}={pid_d!r}'

            elif cmd == 'hipwr_lcs':
                intP1 = int(p1 - 1)
                sns_num = self.hi_pwr_htrs[intP1].sns_num
                retData = f'hi_pwr_lcs_{int(p1)}={sns_num!r}'

            elif cmd == 'hipwr_mode':
                mode = self.hi_pwr_htrs[int(p1)-1].mode
                retData = f'hipwr_mode_{int(p1)}={mode!r}'

            elif cmd == 'hipwr_setpoint':
                intP1 = int(p1 - 1)
                setpoint = self.hi_pwr_htrs[intP1].setPoint
                retData = f'hipwr_setpoint_{int(p1)}={setpoint!r}'

            elif cmd == 'hipwr_state':
                state = self.hi_pwr_htrs[int(p1-1)].status()
                retData = f'hipwr_state_{int(p1)}={state!r}'

            elif cmd == 'hipwr_hysteresis':
                intP1 = int(p1 - 1)
                hysteresis = self.hi_pwr_htrs[intP1].hysteresis
                retData = f'hipwr_hysteresis_{int(p1)}={hysteresis!r}'

            elif cmd == 'hipwr_max_temp':
                intP1 = int(p1 - 1)
                hipwr_max_temp = self.hi_pwr_htrs[intP1].max_temp
                retData = f'hipwr_max_temp_{int(p1)}={hipwr_max_temp!r}'
            
            elif cmd == 'hipwr_min_temp':
                intP1 = int(p1 - 1)
                hipwr_min_temp = self.hi_pwr_htrs[intP1].min_temp
                retData = f'hipwr_min_temp_{int(p1)}={hipwr_min_temp!r}'

            elif cmd == 'hipwr_current':
                if p1 == 1:
                    retData = 'hipwr_current_1='+str(self.tlm['hipwr_current_1'])
                elif p1 == 2:
                    retData = 'hipwr_current_2='+str(self.tlm['hipwr_current_2'])
                else:
                    retData = f'BAD,command failure: unknown arg {p1!r}'

            elif cmd == 'sns_type':
                sns = int(p1 - 1)
                sns_type = self.adcList[sns].sns_type
                retData = f'sns_type_{int(p1)}={sns_type}'

            elif cmd == 'sns_units':
                sns = int(p1 - 1)
                sns_units = self.adcList[sns].sns_units
                if sns_units == 0:
                    units = 'K'
                elif sns_units == 1:
                    units = 'C'
                elif sns_units == 2:
                    units = 'F'
                retData = f'sns_units_{int(p1)}={units}'

            elif cmd == 'sns_cal_coeffs':
                sns = int(p1 - 1)
                calCoeffs = self.adcList[sns].get_calibration_coeffs()
                retData = f'sns_cal_coeffs{int(p1)}={calCoeffs}'

            elif cmd == 'sns_temp':
                sns = str(p1)
                sns = sns.split('.')[0]
                snsName = 'sns_temp_'+sns
                temp = self.tlm[snsName]
                sns_units = self.adcList[int(p1)-1].sns_units
                retData = f'sns_temp_{sns}={temp!r}{sns_units}'

            elif cmd == 'sns_res':
                sns = str(p1)
                sns = sns.split('.')[0]
                snsName = 'sns_res_'+sns
                res = self.tlm[snsName]
                retData = f'sns_res_{sns}={res!r}'

            elif cmd == 'sns_volts':
                sns = str(p1)
                sns = sns.split('.')[0]
                snsName = 'sns_volts_'+sns
                volts = self.tlm[snsName]
                retData = f'sns_volts_{sns}={volts!r}'

            elif cmd == 'adc_filt':
                pass

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

        except Exception as e1:
            retData = 'BAD,command failure: expected args float or int'
            self.logger.error(retData)
            return retData

    async def legacy_command_parser(self, cmdStr):
        retData = 'legacy_command_parser is not complete'
        return retData

    async def enqueue_xmit(self, msg):
        await self.qXmit.put(msg)

    def enqueue_udp(self, msg):
        self.qUDP.put(msg)