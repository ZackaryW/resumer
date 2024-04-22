
from functools import cache
import json
import os
import toml
import yaml

builtinStructNames = ["alias"]
mod_path = os.path.dirname(__file__)

def actual_load(path : str):
    with open(path) as f:
        if path.endswith(".toml"):
            return toml.load(f)
        elif path.endswith(".json"):
            return json.load(f)
        else:
            return f.read()
    

@cache
def loadFile(path : str):
    if path.endswith(".toml"):
        guess = "presets"
    else:
        guess = "data"

    if os.path.exists(os.path.join(mod_path, guess,path)):
        return actual_load(os.path.join(mod_path, guess,path))
    else:
        return actual_load(path)
    
_placeholder = object()

def checkType(data :dict, struct : dict):
    for k, v in data.items():
        if k in builtinStructNames:
            continue

        etype = struct.get(k, _placeholder)
        if etype is _placeholder:
            continue

        if etype == "str":
            assert isinstance(v, str)
        elif etype == "int":
            assert isinstance(v, int)
        elif etype == "float":
            assert isinstance(v, float)
        elif etype == "bool":
            assert isinstance(v, bool)
        elif etype == "list":
            assert isinstance(v, list)
        elif etype == "dict":
            assert isinstance(v, dict)
        elif not etype:
            assert v is None

def yamlToMd(data : dict):
    with open('input.md', 'w') as f:
        f.write("---\n")
        yaml.dump(data, f, default_flow_style=False)
        
        f.write("---\n")