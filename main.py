from app import app
from app.http import message
import json

server = app.WebApp()

def hello_world(args: dict):
    return "Hello world"

def json_data(args: dict):
    print("Data sending")
    data = {
        "message": "This is a JSON response",
        "numbers": [1, 2, 3, 4, 5],
        "boolean": True
    }
    json_body = json.dumps(data)
    
    return json_body

# Register routes
server.add_route("GET", "/hello", hello_world)
server.add_route("GET", "/json", json_data)

if __name__ == "__main__":
    server.run("localhost", 3030)