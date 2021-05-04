import logging
import asyncio

class TCPServer():
    def __init__(self, hostname, port):
        self.logger = logging.getLogger('smb')
        self.qCmd = asyncio.Queue()
        self.qXmit = asyncio.Queue()
        self.hostname = hostname
        self.port = port
    
    async def start(self):
        server = await asyncio.start_server(self.handle_client, self.hostname, self.port)
        addr = server.sockets[0].getsockname()
        self.logger.info('listening: %s', addr)

        async with server:
            await server.serve_forever()

    async def handle_client(self, reader, writer):
        await asyncio.gather(self.cmd_loop(reader, writer), self.xmit_loop(reader, writer))        

    async def cmd_loop(self, reader, writer):
        request = None
        
        while True:        
            try:
                data = await reader.read(100)
                message = data.decode()
                addr = writer.get_extra_info('peername')
                self.logger.info(f'received: {message!r} from {addr!r}')
                asyncio.create_task(self.enqueue_cmd(message))
                await writer.drain()

            except Exception as e2:
                self.logger.error('Unexpected error: ', e2)

            await writer.drain()

        await writer.drain()
        writer.close()

    async def xmit_loop(self, reader, writer):
        while True:
            msg = await self.qXmit.get()
            addr = writer.get_extra_info('peername')
            self.logger.info(f'sending: {msg!r} to {addr!r}')
            writer.write(msg.encode())

    async def enqueue_cmd(self, message):
        await self.qCmd.put(message)
