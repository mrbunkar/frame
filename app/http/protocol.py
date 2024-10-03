import asyncio
import h11
import traceback
import logging
import json
from .message import Request, Response
import logging

class HttpProtocol(asyncio.Protocol):

    def __init__(self, request_handler, event: asyncio.Event) -> None:
        self.h11_conn = h11.Connection(h11.SERVER)
        self.transport = None
        self.request_handler = request_handler
        self.current_request = None
        self.current_request_body = b""
        self.shutdown_event = event
        self.logger = logging.getLogger('HttpProtocol')

    def connection_made(self, transport: asyncio.Transport):
        peername = transport.get_extra_info("peername")
        logging.debug(f"Connection from {peername}")
        self.transport = transport

    def data_received(self, data: bytes) -> None:
        try:
            self.h11_conn.receive_data(data)
            while True:
                event = self.h11_conn.next_event()
                if event is h11.NEED_DATA:
                    break
                self.handle_event(event)
        except Exception as e:
            logging.error(f"Error processing request: {str(e)}")
            self._handle_error(500, "Internal Server Error")

    def handle_event(self, event):
        try:
            if isinstance(event, h11.Request):
                self.current_request = event
            elif isinstance(event, h11.Data):
                self.current_request_body += event.data
            elif isinstance(event, h11.EndOfMessage):
                asyncio.ensure_future(self.process_request())
        except Exception as e:
            self._handle_error(500, f"Error handling event: {str(e)}")

    async def process_request(self):
        if self.current_request:
            request = Request.create_from_h11(
                request=self.current_request,
                body=self.current_request_body
            )
            
            try:
                response = await self.request_handler(request)
                if not isinstance(response, Response):
                    self._handle_error(500, "Internal Server Error")
                    return

                self.send_response(response)
            except Exception as err:
                logging.error(f"Error processing request: {err}")
                self._handle_error(500, "Internal Server Error")
            finally:
                self.current_request = None
                self.current_request_body = None


    def send_response(self, response: Response):
        try:
            logging.info(response)

            data_byte = response.bytes(conn=self.h11_conn)
            self.write_to_transport(data_byte)
        except Exception as e:
            logging.error("error sending response",e)
            self._handle_error(500, "Internal Server Error")

    def write_to_transport(self, data: bytes):
        if not self.shutdown_event.is_set():
            try:
                self.transport.write(data)
                self.h11_conn.start_next_cycle()
                self.transport.write_eof()

            except Exception as err:
                logging.error(f"Error writing to transport: {err}")
                self.connection_lost()
        else:
            self.transport.write_eof()


    def connection_lost(self, exc):
        if exc:
            print(f"Error: {exc}")


    def _handle_error(self, status_code: int, message:str):
        try:
            response = Response(
                content_type="text/plain",
                length=len(message),
                body=message.encode(),
                status_code=status_code
            )
            self.send_response(response)
        except Exception as e:
            logging.error(f"Error sending error response: {e}")
            self.connection_lost()