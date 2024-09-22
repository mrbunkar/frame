import asyncio
from .http.transport import HttpTransport
from .router.handler import handle_request

import logging
logging.basicConfig(level=logging.DEBUG)

class Peer:

    pass

class Transport:

    # Abstract class for all the Transport class: Http and Websockets

    def __init__(self):
        pass

    @staticmethod
    async def server(host, port, transport_type = "http"):

        """
        Starts the TCP transport on the given port and host number
        """     
        if transport_type == "http":
            transport = HttpTransport(
                host=host, 
                port=port,
                request_handler=handle_request
            )
            await transport.start_and_listen()
            return transport
        elif transport_type == "WebSocket":
            logging.warning("WebSocket transport not implemented yet")
            return None
        else:
            logging.error("Invalid protocol type")
            return None
        




