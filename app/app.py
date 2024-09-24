from .transport import Transport
import asyncio

class WebApp:

    def __init__(self) -> None:
        self.transport = None
        self._loop = asyncio.get_event_loop()

    def run(self, host, port, protocol = "http"):
        try:
            self._loop.run_until_complete(self.listen_and_server(host, port, protocol)) # this is the task that is pending
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

        await self.transport.start_and_listen()

    async def shutdown(self):
        print("Manual shutdown")
        if self.transport:
            try:
                await self.transport.close()
            except Exception as err:
                print("Error1:", err)
        self._loop.close()
    
    def add_routes(func, methods: list):
        pass

    @property
    def address(self):
        return f"{self.host}:{self.port}"