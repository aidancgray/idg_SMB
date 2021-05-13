import logging
import asyncio
import sys

class TCPServer():
    def __init__(self, hostname, port):
        self.logger = logging.getLogger('smb')
        self.qCmd = asyncio.Queue()
        self.qXmit = asyncio.Queue()
        self.hostname = hostname
        self.port = port
    
    async def start(self):
        server = await asyncio.start_server(
            client_connected_cb=self.handle_client, 
            host=self.hostname, 
            port=self.port)
        addr = server.sockets[0].getsockname()
        self.logger.info('listening on: %s', addr)

        async with server:
            await server.serve_forever()

    async def handle_client(self, reader, writer):
        await self.cmd_loop(reader, writer)

    async def cmd_loop(self, reader, writer):
        request = None
        cmdLoopCheck = True
        addr = writer.get_extra_info('peername')
        self.logger.info(f'new connection: {addr!r}')
                
        while cmdLoopCheck:        
            try:
                data = await reader.read(100)
                message = data.decode()
                self.logger.info(f'received: {message!r} from {addr!r}')
                
                if message.lower() == 'q\r\n':
                    cmdLoopCheck = False
                    asyncio.create_task(self.enqueue_xmit((writer, 'closing connection...\n')))
                    await asyncio.sleep(0.1)
                else:
                    asyncio.create_task(self.enqueue_cmd((writer, message)))
                    await writer.drain()

            except Exception as e2:
                self.logger.error('Unexpected error: ', e2)
                await writer.drain()
        
        await writer.drain()
        writer.close()

    async def enqueue_cmd(self, message):
        await self.qCmd.put(message)

    async def enqueue_xmit(self, message):
        await self.qXmit.put(message)