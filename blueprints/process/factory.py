from blueprints.process.pipeline import DataPipeline
from typing import *

pipeline_creation_funcs: dict[str, Callable[..., DataPipeline]] = {}

def register(pipeline_type: str, creation_func: Callable[..., DataPipeline]):
    """ register a new Pipeline """
    pipeline_creation_funcs[pipeline_type] = creation_func

def unregister(pipeline_type: str):
    """ Unregister a pipeline """
    pipeline_creation_funcs.pop(pipeline_type, None)

def create(arguments: dict[str, Any]) -> DataPipeline:
    """ Create a new type of Pipeline """ 
    args_copy = arguments.copy()
    pipeline_type = args_copy.pop("type")
    try: 
        creation_func = pipeline_creation_funcs[pipeline_type]
        return creation_func(**args_copy)
    except KeyError:
        raise ValueError(f"Unknwon pipeline type {pipeline_type!r}") from None
