from app.router.routes import GetRoute
import asyncio
from app.http import message


async def test_routes():

    async def func1(args: dict):
        id = int(args['id'])
        await asyncio.sleep(id)
        return "Hello world"

    route = GetRoute(
        "GET",
        path = "/a/b/<id>",
        endpoint=func1
    )

    request = message.Request(
        method="GET",
        target="/a/b/?id=2",
        body = b"Hello world",
        headers="",
        id = 1
    )
    result = await route.handle_request(request=request)

    print(result)

asyncio.run(test_routes())