from dataclasses import dataclass,field


@dataclass(slots=True)
class Request:
    
    method:str
    path:str
    headers:dict
    body:bytes
    query_params: dict = field(default_factory=dict)
    
    
    
