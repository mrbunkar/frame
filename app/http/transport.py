import asyncio
from .protocol import HttpProtocol
import logging

class HttpTransport:

    def __init__(self, host, port, request_handler):
        self.host = host
        self.port = port
        self.request_handler = request_handler
        self.shutdown_event = asyncio.Event()
        self.shutdown_event.clear()
        self.connections = set()
    
    async def start_and_listen(self):
        loop = asyncio.get_event_loop()
        self._loop = loop
        self.server = await loop.create_server(
            lambda: HttpProtocol(self.request_handler, self.shutdown_event, self.connections),
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
        print("Closing")
        self.shutdown_event.set()

        print("Active connection:", len(self.connections))
        for conn in self.connections:
            print("Closing")
            
            # try:
            #     conn.close()
            #     print("Sending EOF")
            # except Exception as err:
            #     logging.error("Error closing connections", err)
        
        print("Active connection after:", len(self.connections))

        if self.server:
            await self.server.wait_closed()
            self.server.close()
