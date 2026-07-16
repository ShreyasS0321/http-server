from dataclasses import dataclass


@dataclass(slots=True)
class Request:
    
    method:str
    path:str
    headers:dict
    body:bytes
    
    
    
