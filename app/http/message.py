from dataclasses import dataclass
import h11

"""
Define message protocol for internal working of application

"""
@dataclass
class Request:
    method: str
    target: str
    headers: dict
    body: bytes

    def create_bytes(self):
        pass

@dataclass
class Response:
    content_type: str
    length: str
    body: bytes

    def create_bytes(self):
        pass

