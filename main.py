from app import app
from app.http import message
import json

server = app.WebApp()

def hello_world(request: message.Request, args: dict):
    return "Hello world"

def json_data(request: message.Request, args: dict):
    data = {
        "message": "This is a JSON response",
        "numbers": [1, 2, 3, 4, 5],
        "boolean": True
    }
    json_body = json.dumps(data).encode('utf-8')
    
    return json_body

# Register routes
server.add_route("GET", "/hello", hello_world)
server.add_route("GET", "/json", json_data)

if __name__ == "__main__":
    server.run("localhost", 3030)