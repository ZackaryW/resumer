from functools import cache
import pkgutil
import importlib

@cache
def list_submodules():
    pkgs = []
    package = importlib.import_module('resumer.profiles')
    for importer, modname, ispkg in pkgutil.iter_modules(package.__path__, package.__name__ + '.'):
        pkgs.append(modname)

    return pkgs

def get_profile(name : str):
    for n in list_submodules():
        if n.split('.')[-1] == name:
            mod = importlib.import_module(n)
            return mod.generate
        