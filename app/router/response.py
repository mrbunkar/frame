from app.http import message

def create_response():
    pass

def server_error():

    body = b"Internal Server Error"
    return message.Response(
        content_type="text/plain",
        status_code=500,
        body=body,
        length=len(body)
    )

def not_supported_response() -> message.Response:
    pass

def method_not_supported() -> message.Response:
    body = b"Method not supported"
    return message.Response(
        content_type= "text/plain",
        status_code=405,
        body = body,
        length=len(body)
    )

def path_not_found() -> message.Response:
    body = b"Path Not found"

    return message.Response(
        content_type= "text/plain",
        status_code=404,
        body = body,
        length=len(body)
    )