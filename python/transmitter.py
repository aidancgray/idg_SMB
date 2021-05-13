import asyncio
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