from functools import wraps

TRANSPILER = [None]
UTILS = {}

def set_transpiler(transpiler):
    TRANSPILER[0] = transpiler

def util(name):
    if name not in UTILS:
        raise KeyError(f"Util {name} needs a definition (@new_util)")

    UTILS[name][0](name)
    return f"__sea_util_{name}__"

def new_util(name):
    def decorator(func):
        @wraps(func)
        def wrapper(name):
            if UTILS[name][1]: return
            UTILS[name][1] = True

            definition = func(f"__sea_util_{name}__")
            TRANSPILER[0].header(f"{definition}")

        if name not in UTILS:
            UTILS[name] = [wrapper, False]

        return wrapper
    return decorator
