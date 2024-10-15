from typing import OrderedDict
from app.http import message
import logging
import asyncio
from typing import Callable, Dict
from urllib.parse import parse_qs, urlparse
from app.router import response
from dataclasses import dataclass
from typing import Callable, Tuple, get_type_hints
from .routes import PostRoute,GetRoute, AbstractRoute

#@TODO Debunk the Route classe into GET,POST, UPDATE and DELETE class
        

class Router:

    """
    Implments the route handling and routing logic for the framework
    """


    def __init__(self) -> None:
        self.routes: Dict[str, Callable] = {}
        self.methods = ["GET", "POST"]


    def add_route(self, full_path: str,route: AbstractRoute) -> None: 
       byte = route.encode()
       self.routes[byte] = route

    def add_get(self, path: str, func: Callable):
        path = f"GET{path}"
        route = GetRoute(
            method = "GET",
            resource=path,
            endpoint=func
        )

        self.add_route(route)

    def add_post(self, path: str, func: Callable) -> None:
        path = f"POST{path}"
        # @TODO: refactore
        route = PostRoute(
            method="POST",
            resource=path,
            endpoint=func
        )
        self.add_route(route)


    def _parse_query_params(self, url: str) -> dict:
        """Extract query parameters from the URL."""

        parsed_url = urlparse(url)
        return parse_qs(parsed_url.query)
    

    def parse_get(self, request: message.Request):
        url_path = request.target.split("?")[0]
        path_with_method = f"{request.method}{url_path}"

        if not path_with_method in self.routes.keys():
            return None, None, "Path Not found"
        
        callable = self.routes[path_with_method]
        query_params = self._parse_query_params(request.target)

        return query_params, callable, None


    def parse_post(self, request: message.Request):
        pass


    async def _process_request(self, request: message.Request) ->  message.Response:
        
        path, is_query = self.resolve_path(request.target)
        hashPath = 


        match request.method:
            case "GET":
                args, callable, err = self.parse_get(request)
            case "POST":
                args, callable, err = self.parse_post(request)
        


    def _method_supported(self, method: str) -> bool:
        return method in self.methods


    async def handle_request(self, request: 'message.Request') -> 'message.Response':
        logging.debug(f"Request: /{request.method}, Target: {request.target}")
        
        try:
            if not self._method_supported(request.method):
                return response.not_supported_response()
            
            resp = await self._process_request(request)
            return resp
        except Exception as err:
            logging.error(f"Exception during processing request: {request.id}")
            return response.server_error()