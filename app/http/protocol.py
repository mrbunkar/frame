import asyncio
import h11
import io

class HttpProtocol(asyncio.Protocol):


    def __init__(self, request_handler, event: asyncio.Event) -> None:
        self.conn = h11.Connection(h11.SERVER)
        self.transport = None
        self.request_handler =request_handler
        self.current_request = None
        self.current_request_body = None
        self.shutdown_event = event
        self.loop = asyncio.get_event_loop()


    def connection_made(self, transport: asyncio.Transport):
        peername = transport.get_extra_info("peername")
        print(f"Connection from {peername}")
        self.transport = transport


    def data_received(self, data: bytes) -> None:
        
        self.conn.receive_data(data)

        while True:
            event = self.conn.next_event()
            if event is h11.NEED_DATA:
                break

            self.handle_event(event)
        
    def handle_event(self, event):
        if isinstance(event, h11.Request):
            self.current_request = event
            self.current_request_body = b""
        elif isinstance(event, h11.Data):
            self.current_request_body += event.data
        elif isinstance(event, h11.EndOfMessage):
            
            self.loop.create_task(self.process_request())

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
                print(f"Error handling request: {err}")
            finally:
                self.current_request = None
                self.current_request_body = None


    def send_response(self, response_data: dict):

        headers = [
            ("Content-Type", response_data.get("content_type")),
            ("Content-Length", str(len(response_data["body"]))),
        ]
        response = h11.Response(
            status_code=response_data["status"],
            headers=headers,
        )
        body = h11.Data(
            data=response_data['body'].encode()
        )

        data_byte = b"".join([
            self.conn.send(response),
            self.conn.send(body),
            self.conn.send(h11.EndOfMessage())
        ])
        self.write_to_transport(data_byte)
        return


    def write_to_transport(self, data):
        # @TODO stream of data, If large chunk of data
        if not self.shutdown_event.is_set():  # Only write if not shutting down
            self.transport.write(data)
            self.conn.start_next_cycle()
        return
    
    async def connection_lost(self):
        # @TODO closing the shutdown gracefully
        # How to run the coroutines
        # this coroutine should run is background
        while True:
            print("Something")
            if self.shutdown_event.is_set():
                self.loop.close()
                self.transport.close()
                return
            asyncio.sleep(0.1)

    def _send_error_response(self):
        # @TODO
        pass
