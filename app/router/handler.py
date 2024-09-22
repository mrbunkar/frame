from typing import OrderedDict

async def handle_request(request):
    print("Receieved request:", request)

    return {
        "status": 200,
        "content_type": "text/plain",
        "body": "Hello, World!"
    }