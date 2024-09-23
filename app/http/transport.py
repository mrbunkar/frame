import asyncio
from .protocol import HttpProtocol

class HttpTransport:

    def __init__(self, host, port, request_handler):
        self.host = host
        self.port = port
        self.request_handler = request_handler
        self.shutdown_event = asyncio.Event()
        self.shutdown_event.clear()
    
    async def start_and_listen(self):
        loop = asyncio.get_event_loop()
        self._loop = loop
        self.server = await loop.create_server(
            lambda: HttpProtocol(self.request_handler, self.shutdown_event),
            host=self.host,
            port=self.port
        )
        
        print(f"Server running on {self.host}:{self.port}")
        
        try:
            async with self.server:
                await self.server.serve_forever()
        except asyncio.CancelledError:
            pass

    def sendfile(self, data):
        pass
    
    async def close(self):
        self.shutdown_event.set()

        if self.server:
            self.server.close()
            await self._loop.run_until_complete(self.server.wait_closed())
        self._loop.stop()
