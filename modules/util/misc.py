VERBOSE = [False]

def check_verbose(options):
    if "v" in options:
        VERBOSE[0] = True

def printv(*args, **kwargs):
    if VERBOSE[0]:
        print(*args, **kwargs)

class MatchIn:
    def __init__(self, obj):
        self.obj = obj

    def __eq__(self, other):
        return self.obj in other

def last_enumerate(iterable, **kwargs):
    for i, thing in enumerate(iterable, **kwargs):
        at_last = i == len(iterable) - 1
        yield at_last, thing
