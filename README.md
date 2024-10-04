
## Frame ##
Is a light weight web framework.
- this is a WIP

- TODO: favicon and message handling

**Benchmark for simple GET method**
- Completed 10000 requests in 1.78 seconds
- Average time per request: 0.0002 seconds
- Successful requests: 10000
- Failed requests: 0
- Timed out requests: 0
  : Code on which test are being run:
    `from app import app
    from app.http import message
    import json

    server = app.WebApp()

    def hello_world(request: message.Request, args: dict) -> message.Response:
        return message.Response(
            content_type="text/plain",
            status_code=200,
            body=b"Hello, World!",
            length=13
        )

    def json_data(request: message.Request, args: dict) -> message.Response:
        data = {
            "message": "This is a JSON response",
            "numbers": [1, 2, 3, 4, 5],
            "boolean": True
        }
        json_body = json.dumps(data).encode('utf-8')
        return message.Response(
            content_type="application/json",
            status_code=200,
            body=json_body,
            length=len(json_body)
        )

    # Register routes
    server.add_route("GET", "/hello", hello_world)
    server.add_route("GET", "/json", json_data)

    if __name__ == "__main__":
        server.run("localhost", 3030)`