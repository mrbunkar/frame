from app.http import message
import json
import mimetypes
from typing import Union, Any
 

def create_response( content: Union[str, bytes, dict, Any],
                    status_code: int = 200,
                    content_type: str = None
                    ) -> message.Response:
    if isinstance(content, dict):
        body = json.dumps(content).encode('utf-8')
        content_type = content_type or 'application/json'
    elif isinstance(content, str):
        body = content.encode('utf-8')
        content_type = content_type or 'text/plain'
    elif isinstance(content, bytes):
        body = content
        content_type = content_type or 'application/octet-stream'
    else:
        body = str(content).encode('utf-8')
        content_type = content_type or 'text/plain'

    return message.Response(
        content_type=content_type,
        status_code=status_code,
        body=body,
        length=len(body)
    )


def working_response(output: Any, status_code: int = 200) -> message.Response:
    return create_response(output, status_code=status_code)


def server_error() -> message.Response:
    return create_response("Internal Server Error", status_code=500)


def not_supported_response() -> message.Response:
    return create_response("Method Not Allowed", status_code=405)
method_not_supported = not_supported_response

def bad_request() -> message.Response:
    return create_response("Bad Request", 400)


def path_not_found() -> message.Response:
    return create_response("Path Not Found", status_code=404)


def serve_file(file_path: str) -> message.Response:
    try:
        with open(file_path, 'rb') as file:
            content = file.read()
        content_type, _ = mimetypes.guess_type(file_path)
        return create_response(content, content_type=content_type or 'application/octet-stream')
    except FileNotFoundError:
        return path_not_found()
    except Exception:
        return server_error()

# Placeholder for WebSocket support
def websocket_handshake(request: message.Request) -> message.Response:
    # Implement WebSocket handshake logic here
    pass