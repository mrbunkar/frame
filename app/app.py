from .transport import Transport
import asyncio

class WebApp:

    def __init__(self) -> None:
        self.transport = None
        self.shutdown_event = asyncio.Event()

    def run(self, host, port, protocol = "http"):
        try:
            asyncio.run(self.listen_and_server(host, port, protocol))
        except KeyboardInterrupt:
            print("Received exit signal. Shutting down gracefully...")
            asyncio.run(self.shutdown())

    async def listen_and_server(self, host, port, protocol = "http"):
        self.host = host
        self.port = port

        self.transport = await Transport.server(
            host=self.host,
            port = self.port,
            transport_type= protocol
        )

    async def shutdown(self):
        self.shutdown_event.set()

        if self.transport:
            await self.transport.close()
    
    def add_routes(func, methods: list):
        pass

    @property
    def address(self):
        return f"{self.host}:{self.port}"