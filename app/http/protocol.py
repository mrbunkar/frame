import asyncio
import h11
import traceback
import logging
import json

class HttpProtocol(asyncio.Protocol):
    def __init__(self, request_handler, event: asyncio.Event, loop: asyncio.BaseEventLoop) -> None:
        self.conn = h11.Connection(h11.SERVER)
        self.transport = None
        self.request_handler = request_handler
        self.current_request = None
        self.current_request_body = None
        self.shutdown_event = event
        self.loop = loop
        self.logger = logging.getLogger('HttpProtocol')

    def connection_made(self, transport: asyncio.Transport):
        peername = transport.get_extra_info("peername")
        print(f"Connection from {peername}")
        self.transport = transport

    def data_received(self, data: bytes) -> None:
        print("Data received")
        try:
            self.conn.receive_data(data)
            while True:
                event = self.conn.next_event()
                if event is h11.NEED_DATA:
                    break
                self.handle_event(event)
        except Exception as e:
            self._handle_error(500, f"Error processing request: {str(e)}")

    def handle_event(self, event):
        try:
            if isinstance(event, h11.Request):
                self.current_request = event
                self.current_request_body = b""
            elif isinstance(event, h11.Data):
                self.current_request_body += event.data
            elif isinstance(event, h11.EndOfMessage):
                self.loop.create_task(self.process_request())
        except Exception as e:
            self._handle_error(500, f"Error handling event: {str(e)}")

    async def process_request(self):
        if self.current_request:
            request = {
                'method': self.current_request.method.decode(),
                'target': self.current_request.target.decode(),
                'headers': dict(self.current_request.headers),
                'body': self.current_request_body
            }
            
            try:
                data = await self.request_handler(request)
                self.send_response(data)
            except Exception as err:
                self.handle_application_error(err)
            finally:
                self.current_request = None
                self.current_request_body = None

    def send_response(self, response_data: dict):
        try:
            headers = [
                ("Content-Type", response_data.get("content_type", "text/plain")),
                ("Content-Length", str(len(response_data["body"]))),
            ]
            response = h11.Response(
                status_code=response_data["status"],
                headers=headers,
            )
            body = h11.Data(data=response_data['body'].encode())
            end = h11.EndOfMessage()

            data_byte = b"".join([
                self.conn.send(response),
                self.conn.send(body),
                self.conn.send(end)
            ])
            self.write_to_transport(data_byte)
        except Exception as e:
            self._handle_error(500, f"Error sending response: {str(e)}")


    def write_to_transport(self, data):
        if not self.shutdown_event.is_set():
            try:
                print("Bytes: ", data)
                self.transport.write(data)
                self.conn.start_next_cycle()
                self.transport.write_eof()  # to close the connection
            except Exception as err:
                print(f"Error writing to transport: {err}")
                self._handle_error(500, "Internal Server Error")


    def connection_lost(self, exc):
        print("Connection lost")
        if exc:
            print(f"Error: {exc}")
    
    def handle_application_error(self, err):
        error_message = f"Application error: {err}\n{traceback.format_exc()}"
        self.logger.error(error_message)
        # Assuming the application defines its own error responses
        self._send_error_response(500, str(err))

    def handle_framework_error(self, err):
        error_message = f"Framework error: {err}\n{traceback.format_exc()}"
        self.logger.critical(error_message)
        self._send_generic_error_response()

    def _send_error_response(self, status_code, message):
        try:
            status_phrase = {
                400: "Bad Request",
                401: "Unauthorized",
                403: "Forbidden",
                404: "Not Found",
                500: "Internal Server Error",
                # Add more as needed
            }.get(status_code, "Unknown Error")

            error_body = json.dumps({
                "error": {
                    "code": status_code,
                    "message": message
                }
            })

            headers = [
                ("Content-Type", "application/json"),
                ("Content-Length", str(len(error_body))),
            ]
            error = h11.Response(
                status_code=status_code,
                reason=status_phrase.encode(),
                headers=headers,
            )
            body = h11.Data(data=error_body.encode())
            end = h11.EndOfMessage()

            data_byte = b"".join([
                self.conn.send(error),
                self.conn.send(body),
                self.conn.send(end)
            ])
            self.write_to_transport(data_byte)
        except Exception as e:
            # If sending a detailed error response fails, fall back to generic error
            self.logger.critical(f"Failed to send error response: {e}\n{traceback.format_exc()}")
            self._send_generic_error_response()


    def _send_generic_error_response(self):
        try:
            generic_error = b"HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/plain\r\nContent-Length: 21\r\n\r\nInternal Server Error\n"
            self.transport.write(generic_error)
            self.transport.write_eof()
        except Exception as e:
            self.logger.critical(f"Failed to send generic error response: {e}\n{traceback.format_exc()}")


    def _handle_error(self, status_code, message):
        try:
            error_response = {
                "status": status_code,
                "content_type": "text/plain",
                "body": message
            }
            self.send_response(error_response)
        except Exception as e:
            print(f"Error sending error response: {e}")


    # def _send_error_response(self, status_code, message):
    #     headers = [
    #         ("Content-Type", "text/plain"),
    #         ("Content-Length", str(len(message))),
    #     ]
    #     error = h11.Response(
    #         status_code=status_code,
    #         headers=headers,
    #     )
    #     body = h11.Data(data=message.encode())
    #     end = h11.EndOfMessage()

    #     data_byte = b"".join([
    #         self.conn.send(error),
    #         self.conn.send(body),
    #         self.conn.send(end)
    #     ])
    #     self.write_to_transport(data_byte)
    #     self.transport.write_eof()
