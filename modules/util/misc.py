class MatchIn:
    def __init__(self, obj):
        self.obj = obj

    def __eq__(self, other):
        return self.obj in other

def last_enumerate(iterable, **kwargs):
    for i, thing in enumerate(iterable, **kwargs):
        at_last = i == len(iterable) - 1
        yield (at_last, thing)

def repr_expand(iterable):
    iterable = [escape_whitespace(obj) for obj in iterable]

    if len(iterable) < 2:
        return repr(iterable[0])

    return ",".join(iterable[:-1]) + f" or {iterable[-1]}"

def escape_whitespace(string):
    if string == "":
        return "EOF"

    return string.replace("\n", r"\n").replace("    ", r"\t")
