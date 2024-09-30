from dataclasses import dataclass

"""
Define message protocol for internal working of application

"""
@dataclass
class Request:
    method:str

