from typing import OrderedDict
from app.http import message
import logging
import asyncio
from typing import Callable, Dict
from urllib.parse import parse_qs, urlparse
from app.router import response

class Router:

    """
    Implments the route handling and routing logic for the framework
    """

    def __init__(self) -> None:
        self.routes: Dict[str, Callable] = {}
        self.methods = ["GET", "POST"]


    def add_route(self, path_with_method: str, func: Callable):
        self.routes[path_with_method] = func


    def add_get(self, path: str, func: Callable):
        path = f"GET{path}"
        self.add_route(path, func)


    def add_post(self, path: str, func: Callable):
        path = f"POST{path}"
        self.add_route(path, func)


    def _parse_query_params(self, url: str) -> dict:
        """Extract query parameters from the URL."""

        parsed_url = urlparse(url)
        return parse_qs(parsed_url.query)
    

    def parse_get(self):
        pass


    async def _process_request(self, request: 'message.Request'):
        return
        # match request.method:
        #     case "GET":
        #         args, callable = pass
        #     case "POST":
        #         args, callable = pass
        

        url_path = request.target.split("?")[0]
        path_with_method = f"{request.method}{url_path}"

        if path_with_method not in self.routes:
            return response.method_not_supported()

        callable = self.routes[path_with_method]
        query_params = self._parse_query_params(request.target)

        if asyncio.iscoroutinefunction(callable):
            return await callable(request, query_params)
        else:
            return callable(request, query_params)


    def _method_supported(self, method: str) -> bool:
        return method in self.methods


    async def handle_request(self, request: 'message.Request') -> 'message.Response':
        print("Received request:", request)
        
        try:
            if not self._method_supported(request.method):
                return response.not_supported_response()
            
            resp = await self._process_request(request)
            return resp
        except Exception as err:
            logging.error(f"Exception during processing request: {request.id}")
            return response.server_error()