import asyncio
from typing import Callable,get_type_hints
from app.http import message
from app.router import response
import logging
import json

def url_hash(method: str, url: str) -> bytes:
    """
    Given a URL and method will give Hash of the URL.
    @TODO: for only giving encoded string
    """
    path: str
    path, is_query = resolve_path(url)
    return " ".join(
        method.encode(),
        path.encode(),
        is_query
    )

def resolve_path(path: str) -> tuple[str, bool]:
        """
        Will seperate path and query parameter if any.

        Return: Path and True if query paramtetr availble else False

        example: 
          1. input: path = /a/b/?id=1, output: /a/b, True
          2. input: path = /a/c,      output: /a/c, False
        """
        
        if '<' in path:
            return path.split('/<')[0], True
        
        return path, False

class AbstractRoute:

    def __init__(self, method: str, path: str, endpoint: Callable) -> None:
        
        self.method: str = method
        self.path: str = path
        self.callable: Callable = endpoint

    def encode(self) -> bytes:
        return NotImplementedError
    
    def register_url(self):
        return NotImplementedError
    
    async def handle_request(self):
        return NotImplementedError


class GetRoute(AbstractRoute):

    def __init__(self, method: str, path: str, endpoint: Callable) -> None:
        super().__init__(method, path, endpoint)
        self._absolute_path: str = None
        self._parameters: list = []
        self.register_url() # Registering URL

        self._is_query_path: bool = len(self._parameters) > 0

    def encode(self):
        return " ".join(
            self.method,
            
        )

    def register_url(self):
        self._unzip_path()

    def _extract_arguments(self, path: str):

        """
        /a/?key=value => Key and Value
        """
        segments = path.split("/?")[1:]
        self._arguments: dict = {}

        for segment in segments:
            if "&" in segment:
                arguments = [value for value in segment.split("&")]
                for args in arguments:
                    k, v = args.split(":")[0], args.split(":")[1]
                    self._arguments[k] = v
            elif ":" in segment:
                k, v = segment.split(":")[0], segment.split(":")[1]
                self._arguments[k] = v
            else:
                raise TypeError
            

    def _arguments_validation(self) -> bool:
        for k in self._arguments: 
            if not k in self._parameters:
                return False
            
            v: str = self._arguments[k]
            if v.isdigit():
                v = int(v)

        return True

    async def handle_request(self, request: message.Request) -> message.Response:
        method = request.method
        
        if method != "GET":
            logging.ERROR(f"Method expected GET, but got {method}")
            return response.server_error()
        
        # URL Arguments checking
        try:
            self._extract_arguments(request.target)
        except Exception as err:
            logging.error("URL arguments formating is wrong")
            return response.bad_request()
        
        if not self._arguments_validation():
            logging.error("Unexpected URL Arguments")
            return response.bad_request()
        
        result = await self.excute_callable(self._arguments)

        if isinstance(result, message.Response):
            return result
        
        return self.create_response(result)
    
    def create_response(self, results) -> message.Response:
        
        if len(results) > 2 :
            logging.error(
                f"Callable function returns {len(results)}. Expected: 2"
            )
            return response.server_error()
        
        if len(results) == 1:
            result, status_code = results, 200
        else:
            result, status_code = results[0], results[1]

        if isinstance(result, dict):
            result_object = json.dump(result) 
            content_type = "application/json"
        else:
            result_object = result
            content_type = "text/plain"

        #@TODO: check for content type
        return message.Response(
            content_type=content_type,
            length=len(result_object.encode()),
            body= result_object.encode(),
            status_code= status_code
        )
        
    
    async def excute_callable(self, **args):
        
        if asyncio.iscoroutinefunction(self.callable):
            return await self.callable(**args)
        else:
            return self.callable(**args)

    def encode(self):
        # We can using Hashing algorithim also
        return b" ".join(
            self.method,
            self._absolute_path,
            self._is_query_path
        )

    def _unzip_path(self) -> None:

        """
        /price/<float:value>/<id> => value,id
        """
        segments = self.path.split("<")
          
        for segment in segments:
            if '>' in segment:
                param_part = segment.split(">")[0]

                if ':' in param_part:
                    param_name = param_part.split(":")[1]      
                else:
                    param_name = param_part
                
                self._parameters.append(param_name)


class PostRoute(AbstractRoute):

    def __init__(self, method: str, path: str, endpoint: Callable[..., Any]) -> None:
        pass