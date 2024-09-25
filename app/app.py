from .transport import Transport
import asyncio

class WebApp:

    def __init__(self) -> None:
        self.transport = None
        self.loop = asyncio.get_event_loop()
       
    def run(self, host, port, protocol="http"):
        try:
            asyncio.run(self.listen_and_server(host, port, protocol))
        except KeyboardInterrupt:
            print("Received exit signal. Shutting down gracefully...")
            asyncio.run(self.shutdown())
        finally:
            self.loop
    
    async def listen_and_server(self, host, port, protocol = "http"):
        self.host = host
        self.port = port

        self.transport = await Transport.server(
            host=self.host,
            port = self.port,
            transport_type= protocol
        )

        # Start listening in an awaitable context
        await self.transport.start_and_listen()

    async def shutdown(self):
        print("Manual shutdown")
        if self.transport:
            try:
                await self.transport.close()
            except Exception as err:
                print("Error during transport close:", err)
    
    def add_routes(func, methods: list):
        pass

    @property
    def address(self):
        return f"{self.host}:{self.port}"