from .transport import Transport
import asyncio
from .router.handler import Router
import logging

class WebApp:

    def __init__(self) -> None:
        self.transport = None
        self.router = Router()
       

    def run(self, host, port, protocol="http"):
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
            transport_type= protocol,
            handler = self.manage_request
        )

        await self.transport.start_and_listen()


    async def shutdown(self):
        print("Manual shutdown")
        if self.transport:
            try:
                await self.transport.close()
            except Exception as err:
                print("Error during transport close:", err)


    async def manage_request(self, request):

        """
        Takes a Request object and gives to middleware and router
        """

        #  @TODO support for middleware
        
        try:
            data = await self.router.handle_request(request)
        except Exception as err:
            logging.exception("Exception during request mgmt")

        return data

    @property
    def address(self):
        return f"{self.host}:{self.port}"
    

    def add_route(self, method: str, routes: str, callback_func):
        if method == "GET":
            self.router.add_get(routes, callback_func)
        elif method == "POST":
            self.router.add_post(routes, callback_func)
        else:
            # TODO: Defince proper exception
            logging.ERROR("Method not supported")
            raise NotImplementedError("Method not supported")

        
