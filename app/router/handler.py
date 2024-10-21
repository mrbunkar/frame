from typing import OrderedDict
from app.http import message
import logging
import asyncio
from typing import Callable, Dict
from urllib.parse import parse_qs, urlparse
from app.router import response
from dataclasses import dataclass
from typing import Callable
from .routes import PostRoute,GetRoute, AbstractRoute, url_hash
        

class Router:

    """
    Implments the route handling and routing logic for the framework
    """

    def __init__(self) -> None:
        self.routes: Dict[str, Callable] = {}
        self.methods = ["GET", "POST"]

    def add_route(self,route: AbstractRoute) -> None: 
       byte = route.encode()
       self.routes[byte] = route

    def add_get(self, path: str, func: Callable):
        route = GetRoute(
            method = "GET",
            path=path,
            endpoint=func
        )
        self.add_route(route)

    def add_post(self, path: str, func: Callable) -> None:
        route = PostRoute(
            method="POST",
            path=path,
            endpoint=func
        )
        self.add_route(route)

    async def _process_request(self, request: message.Request) ->  message.Response:
        logging.debug(f"New Request: ,{request.id}")

        hashPath = url_hash(method=request.method, url = request.target)
        # @TODO coruotine safe 
        if not hashPath in self.routes.keys():
            return response.bad_request()

        route: AbstractRoute = self.routes[hashPath]
        return await route.handle_request(request)

    def _method_supported(self, method: str) -> bool:
        return method in self.methods


    async def handle_request(self, request: 'message.Request') -> 'message.Response':
        logging.debug(f"Request: {request.method}, Target: {request.target}")
        
        try:
            if not self._method_supported(request.method):
                return response.not_supported_response()
            
            resp = await self._process_request(request)
            return resp
        except Exception as err:
            logging.error(f"Exception during processing request: {request.id}")
            return response.server_error()