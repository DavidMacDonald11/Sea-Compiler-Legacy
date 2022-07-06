VERBOSE = [False]

def check_verbose(options):
    if "v" in options:
        VERBOSE[0] = True

def printv(*args, **kwargs):
    if VERBOSE[0]:
        print(*args, **kwargs)
