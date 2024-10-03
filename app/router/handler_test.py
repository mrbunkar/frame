from app.http import message
from app.router.handler import Router
import asyncio

def hello(request, *args):
    print("Hello world!")
    return "Hello"

async def test_handler():
    route = Router()
    route.add_get("/hello", hello)

    request = message.Request(
        method="GET",
        target="/hello",
        headers=[],
        body= b"",
        id = 1,
    )
    
    result = await route.handle_request(request)
    print(result)

asyncio.run(test_handler())
    

