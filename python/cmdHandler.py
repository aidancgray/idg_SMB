import logging
import asyncio
from CMD_DICT import cmd_set_dict, cmd_get_dict
from LEG_CMD_DICT import leg_action_dict, leg_query_dict

class CMDLoop:
    def __init__(self, qCmd, qXmit):
        self.logger = logging.getLogger('smb')
        self.qCmd = qCmd
        self.qXmit = qXmit

    async def start(self):
        while True:
            if not self.qCmd.empty():
                msg = await self.qCmd.get()
                self.logger.info(f'consuming: {msg!r} from qCmd')
                await self.parse_raw_command(msg)

            await asyncio.sleep(1)

    async def parse_raw_command(self, rawCmd):
        cmdStr = rawCmd.strip()  # remove whitespace at the end
        
        if cmdStr[0] == '~' or cmdStr[0] == '?':
            await self.legacy_command_parse(cmdStr)
        
        elif cmdStr[0] == '$':
            cmdStr = cmdStr[1:]  # Remove the start character
            cmdStr = cmdStr.replace(' ', '')  # Remove all whitespace
            cmdStrList = cmdStr.split(',')  # split the command on the commas
            
            if cmdStrList[0] == 'set':
                await self.parse_set_command(cmdStr[1:])

            elif cmdStrList[0] == 'get':
                await self.parse_get_command(cmdStr[1:])

            else:
                err = 'command failure: second arg must be \'set\' or \'get\''
                self.logger.error(err)
                await self.enqueue_xmit(err)

        else:
            err = 'command failure: must start with \'~\', \'?\', or \'$\''
            self.logger.error(err)
            await self.enqueue_xmit(err)

    async def parse_set_command(self, cmdStr):
        if cmdStr[0] in cmd_set_dict:
            cmd_dict = cmd_set_dict[cmdStr[0]]

            # Check if cmd parameters meet cmd_dict requirements
            if cmd_dict['P1_MIN'] == None and cmd_dict['P1_MAX' == None] and cmd_dict['P2_MIN'] == None and cmd_dict['P2_MAX' == None]:
                if len(cmdStr) == 1:
                    await self.execute_set_command(cmd_dict, cmdStr[0], [None, None])
                    
                else:
                    err = 'command failure: This command accepts no args'
                    self.logger.error(err)
                    await self.enqueue_xmit(err)

            elif cmd_dict['P1_MIN'] != None and cmd_dict['P1_MAX' != None] and cmd_dict['P2_MIN'] == None and cmd_dict['P2_MAX' == None]:
                if len(cmdStr) == 2:
                    await self.execute_set_command(cmd_dict, cmdStr[0], [cmdStr[1], None])

                else:
                    err = 'command failure: This command requires 1 arg'
                    self.logger.error(err)
                    await self.enqueue_xmit(err)

            else:
                if len(cmdStr) == 3:
                    await self.execute_set_command(cmd_dict, cmdStr[0], cmdStr[1:3])

                else:
                    err = 'command failure: This command requires 2 args'
                    self.logger.error(err)
                    await self.enqueue_xmit(err)

        else:
            err = 'command failure: cmd arg invalid'
            self.logger.error(err)
            await self.enqueue_xmit(err)
    
    async def parse_get_command(self, cmdStr):
        if cmdStr[0] in cmd_get_dict:
            cmd_dict = cmd_get_dict[cmdStr[0]]
            
            # Check if cmd parameters meet cmd_dict requirements
            if cmd_dict['P1_MIN'] == None and cmd_dict['P1_MAX' == None]:
                if len(cmdStr) == 1:
                    await self.execute_get_command(cmd_dict, cmdStr[0], [None])

                else:
                    err = 'command failure: This command accepts no args'
                    self.logger.error(err)
                    await self.enqueue_xmit(err)

            else:
                if len(cmdStr) == 2:
                    await self.execute_get_command(cmd_dict, cmdStr[0], cmdStr[1:2])

                else:
                    err = 'command failure: This command requires 1 arg'
                    self.logger.error(err)
                    await self.enqueue_xmit(err)

        else:
            err = 'command failure: cmd arg invalid'
            self.logger.error(err)
            await self.enqueue_xmit(err)

    async def execute_set_command(self, cmd_dict, cmd, params):
        p1 = params[0]
        p2 = params[1]
        p1min = cmd_set_dict['P1_MIN']
        p1max = cmd_set_dict['P1_MAX']
        p2min = cmd_set_dict['P2_MIN']
        p2max = cmd_set_dict['P2_MAX']
        output = 'OK'

        # Check p1
        if p1min == None and p1max == None:
            pass
        elif p1min == None and p1 <= p1max:
            pass
        elif p1max == None and p1 >= p1min:
            pass
        elif p1 >= p1min or p1 <= p1max:
            pass
        else:
            err = 'command failure: args out of range'
            self.logger.error(err)
            await self.enqueue_xmit(err)
            return -1

        # Check p2
        if p2min == None and p2max == None:
            pass
        elif p2min == None and p2 <= p2max:
            pass
        elif p2max == None and p2 >= p2min:
            pass
        elif p2 >= p2min or p2 <= p2max:
            pass
        else:
            err = 'command failure: args out of range'
            self.logger.error(err)
            await self.enqueue_xmit(err)
            return -1

        # Handle each command case
        
        if cmd == 'bid':
            pass
        
        elif cmd == 'pid_d':
            pass

        elif cmd == 'rst':
            pass

        elif cmd == 'bb':
            pass

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

        elif cmd == 'htr_cur':
            pass

        elif cmd == 'setpoint':
            pass

        elif cmd == 'excit':
            pass

        else:
            self.logger.error(f'Unknown command: {cmd!r}')
            raise ValueError(f'Unknown command: {cmd!r}')

    async def legacy_command_parse(self, cmdStr):
        pass

    async def enqueue_xmit(self, msg):
        await self.qXmit.put(msg)