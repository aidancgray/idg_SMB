import logging
import asyncio
from CMD_DICT import cmd_set_dict, cmd_get_dict
from LEG_CMD_DICT import leg_action_dict, leg_query_dict
from chebyFit import chebyFit

class CMDLoop:
    def __init__(self, qCmd, qXmit, eeprom, tlm, cal, io, bme280, ads1015, hi_pwr_htrs, dacList):
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

    async def start(self):
        while True:
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

            ### Check the Command Queue ###
            if not self.qCmd.empty():
                msg = await self.qCmd.get()
                writer = msg[0]
                cmd = msg[1]
                retData = await self.parse_raw_command(cmd)
                await self.enqueue_xmit((writer, retData+'\n'))

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
                retData = 'command failure: second arg must be \'set\' or \'get\''
                self.logger.error(retData)

        else:
            retData = 'command failure: must start with \'~\', \'?\', or \'$\''
            self.logger.error(retData)

        return retData

    async def parse_set_command(self, cmdStr):
        if cmdStr[0] in cmd_set_dict:
            cmd_dict = cmd_set_dict[cmdStr[0]]

            # Check if cmd parameters meet cmd_dict requirements
            if cmd_dict['P#'] == 0:
                if len(cmdStr) == 1:
                    retData = await self.execute_set_command(cmd_dict, cmdStr[0], [None, None])
                    
                else:
                    retData = 'command failure: This command accepts no args'
                    self.logger.error(retData)

            elif cmd_dict['P#'] == 1:
                if len(cmdStr) == 2:
                    retData = await self.execute_set_command(cmd_dict, cmdStr[0], [cmdStr[1], None])

                else:
                    retData = 'command failure: This command requires 1 arg'
                    self.logger.error(retData)

            elif cmd_dict['P#'] == 2:
                if len(cmdStr) == 3:
                    retData = await self.execute_set_command(cmd_dict, cmdStr[0], cmdStr[1:3])

                else:
                    retData = 'command failure: This command requires 2 args'
                    self.logger.error(retData)
            else:
                    retData = 'command dictionary failure: Command requires too many args'
                    self.logger.error(retData)
        else:
            retData = 'command failure: cmd arg invalid'
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
                    retData = 'command failure: This command accepts no args'
                    self.logger.error(retData)

            elif cmd_dict['P#'] == 1:
                if len(cmdStr) == 2:
                    retData = await self.execute_get_command(cmd_dict, cmdStr[0], cmdStr[1:2])

                else:
                    retData = 'command failure: This command requires 1 arg'
                    self.logger.error(retData)

            else:
                    retData = 'command dictionary failure: Command requires too many args'
                    self.logger.error(retData)

        else:
            retData = 'command failure: cmd arg invalid'
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
                retData = 'command failure: arg 1 out of range'
                self.logger.error(retData)
                return retData

            # Check p2
            if p2min == None and p2max == None:
                pass
            elif p2min == None and float(p2) <= p2max:
                p1 = float(p1)
            elif p2max == None and float(p2) >= p2min:
                p1 = float(p1)
            elif float(p2) >= p2min and float(p2) <= p2max:
                p1 = float(p1)
            else:
                retData = 'command failure: arg 2 out of range'
                self.logger.error(retData)
                return retData

            # Handle each command case
            
            if cmd == 'id':
                self.tlm['id'] = p1
                retData = 'OK'
            
            elif cmd == 'pid_d':
                pass

            elif cmd == 'rst':
                pass

            elif cmd == 'hi_pwr':
                if int(p2) == 0:
                    self.hi_pwr_htrs[int(p1)-1].power_off()
                elif int(p2) == 1:
                    self.hi_pwr_htrs[int(p1)-1].power_on()
                retData = 'OK'

            elif cmd == 'pid_i':
                pass

            elif cmd == 'lcs':
                pass

            elif cmd == 'htr_ena':
                pass

            elif cmd == 'pid_p':
                pass

            elif cmd == 'adc_filt':
                pass

            elif cmd == 'sns_typ':
                pass

            elif cmd == 'sns_units':
                pass
            
            elif cmd == 'sns_cal':
                sensor = p1
                tmpCalData = p2.split(';')
                calData = []

                for point in tmpCalData:
                    newPt = point.split(' ')
                    calData.append(newPt)

                # convert calData[][0] points from sensor units to bits
                chebyshevFit = chebyFit(calData, 10)
                self.cal[sensor]['coeffs'] = chebyshevFit.chebyFit[0]
                self.cal[sensor]['zl'] = chebyshevFit.chebyFit[1]
                self.cal[sensor]['zu'] = chebyshevFit.chebyFit[2]

            elif cmd == 'htr_cur':
                pass

            elif cmd == 'setpoint':
                pass

            elif cmd == 'excit':
                pass

            # just a couple test functions
            elif cmd == 'test_a':
                retData = '#'+p1+'#'+'@'+p2+'@'

            elif cmd == 'test_b':
                retData = 'Valid'

            else:
                retData = f'command failure: unknown command {cmd!r}'
                self.logger.error(retData)
                return retData

            return retData
        
        except (TypeError, ValueError):
            retData = 'command failure: expected args float or int'
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
                retData = 'command failure: args out of range'
                self.logger.error(retData)
                return retData

            # Handle each command case
            
            if cmd == 'id':
                board_id = self.tlm['id']
                retData = f'id={board_id!r}'
            
            elif cmd == 'pid_d':
                pass

            elif cmd == 'hi_pwr':
                retData = self.hi_pwr_htrs[int(p1)-1].status()

                if retData == 0:
                    retData = 'off'
                elif retData == 1:
                    retData = 'on'
                else:
                    retData = 'GPIO read error'

            elif cmd == 'pid_i':
                pass

            elif cmd == 'lcs':
                pass

            elif cmd == 'sns_tmp':
                pass

            elif cmd == 'htr_ena':
                pass
            
            elif cmd == 'sw_rev':
                pass

            elif cmd == 'pid_p':
                pass

            elif cmd == 'adc_filt':
                pass

            elif cmd == 'sns_typ':
                pass

            elif cmd == 'sns_units':
                pass

            elif cmd == 'htr_cur':
                if p1 == 1:
                    retData = 'htr_current1='+str(self.tlm['htr_current1'])
                elif p1 == 2:
                    retData = 'htr_current2='+str(self.tlm['htr_current2'])
                else:
                    retData = f'command failure: unknown arg {p1!r}'

            elif cmd == 'setpoint':
                pass

            elif cmd == 'excit':
                pass
            
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
                    retData = f'command failure: unknown arg {p1!r}'
            
            # just a couple test functions
            elif cmd == 'test_a':
                retData = '#'+p1+'#'

            elif cmd == 'test_b':
                retData = 'Valid'

            else:
                retData = f'command failure: unknown command {cmd!r}'
                self.logger.error(retData)
                return retData

            return retData

        except TypeError as e1:
            #print(e1)
            retData = 'command failure: expected args float or int'
            self.logger.error(retData)
            return retData

    async def legacy_command_parser(self, cmdStr):
        retData = 'legacy_command_parser is not complete'
        return retData

    async def enqueue_xmit(self, msg):
        await self.qXmit.put(msg)