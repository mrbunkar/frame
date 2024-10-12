import asyncio
from typing import Callable,get_type_hints
from app.http import message
from app.router import response

class Route:

    def __init__(self,method: str, resource: str, endpoint: Callable) -> None:
        self.method: str = method
        self.path: str = resource
        self._callable: Callable = endpoint
        self._parameters: list = []
        self._get_func_types()
        self._is_query_path: bool = None
    
    def encode(self):
        return b" ".join(
            self.method.encode(),
            self.path.encode(),
            self._is_query_path
        )
    
    def _get_func_types(self) -> None:
        types: dict = get_type_hints(self._callable)

        return_types = types['return']
        self._parameter_types = {}
        self._return_types = []
        for key, value in types:
            if key != "return":
                self._parameter_types[key] = value

        for type in return_types:
            self._return_types.append(type)

    def _return_type_check(self, results) -> bool:

        """
        Check for the return types of callable
        """
        for value, type in zip(results, self._return_types):
            if not isinstance(value, type):
                return False
           
        return True

    async def run(self, *args, **kwargs) -> message.Response:
        if asyncio.iscoroutinefunction(self._callable):
            result = await self._callable(args, kwargs)
        else:
            result = self._callable(args, kwargs)

        if not self._return_types(result):
            return response.server_error()
        
        

class GetRoute(Route):

    def __init__(self,method: str, resource: str, endpoint: Callable) -> None:
        super().__init__(method=method, resource=resource, endpoint=endpoint)
        self._unzip_resource()
        self._is_query_path: bool = len(self._parameters) > 0

    def _unzip_resource(self):

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

    def url_arguments(self, path: str) -> dict:

        args_dict: dict = {}
        args_str: list = path.split("/?")[1:]

        for arg in args_str:
            k , v = arg.split(":")

            if v.isdigit():
                v = int(v)
            
            args_dict[k] = v

        return args_dict

    def argument_type_check(self, parameter) -> bool:
        pass

    async def handle(self, request: message.Request):
        
        args = self.url_arguments(self, request.target)

        result = await self.run()

        pass

    def creat_response(self) -> message.Response:
        pass