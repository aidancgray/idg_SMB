# transmitter.py
# 5/24/2021
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# The Transmit Loop. It runs in parallel with the Command Handler and 
# TCP Server loops. It monitors the Transmit Queue for new messages, 
# then sends out the message to the correct client.

import logging

class Transmitter:
    def __init__(self, qXmit):
        self.logger = logging.getLogger('smb')
        self.qXmit = qXmit

    async def start(self):
        while True:
            cmd = await self.qXmit.get()  
            writer = cmd[0]
            msg = cmd[1]
            addr = writer.get_extra_info('peername')
            self.logger.info(f'sending: {msg!r} to {addr!r}')
            writer.write(msg.encode())