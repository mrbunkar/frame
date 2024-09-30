from typing import OrderedDict


class Router:

    def __init__(self) -> None:
        self.routes = {}

    def add_route(self, path_with_method:bytes, func):
        self.routes[path_with_method] = func

    def add_get(self,path:str, func):
        path = "get"+path
        self.add_route(path.encode(), func)

    def add_post(self, path:str, func):
        path = "post"+path
        self.add_route(path.encode(), func)
    
    async def handle_request(self,request):
        print("Receieved request:", request)

        return {
            "status": 200,
            "content_type": "text/plain",
            "body": "Hello, World!"
        }
