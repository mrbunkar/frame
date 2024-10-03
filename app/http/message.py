from dataclasses import dataclass
import h11
import random

"""
Define message protocol for internal working of application
"""



@dataclass
class Request:
    method: str
    target: str
    headers: dict
    body: bytes
    id: int


    def route(self) -> bytes:
        return f"{self.method}{self.target}"


    @classmethod
    def create_from_h11(cls, request: h11.Request, body: bytes):
        """
        Creates a Request object from the bytes
        """
        return cls(
            method=request.method.decode(),
            target=request.target.decode(),
            headers=dict(request.headers),
            body=body,
            id = random.randint(1,10)
        )


class BaseResonse:

    def bytes(self):
        pass


@dataclass
class Response(BaseResonse):
    content_type: str
    length: str
    body: bytes
    status_code: int


    def bytes(self, conn: h11.Connection) -> bytes:

        """
        Create byte representaton of response object to send over the transport
        """
        headers = [
            ("Content-Type", self.content_type),
            ("Content-Length", str(len(self.body))),
        ]

        response = h11.Response(
            status_code=self.status_code,
            headers=headers
        )

        body = h11.Data(data=self.body)
        end = h11.EndOfMessage()
        return b"".join([
            conn.send(response),
            conn.send(body),
            conn.send(end)
        ])


# @dataclass
# class ErrorResponse(BaseResonse):
    