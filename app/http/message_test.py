from app.http.message import Response

def test_response():
    message = "Hello world"
    response = Response(
        content_type="text/plain",
        length=len(message),
        body=message.encode(),
        status_code=200
    )

    print(response.bytes())

test_response()