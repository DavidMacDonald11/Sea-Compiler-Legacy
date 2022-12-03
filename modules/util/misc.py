import re

class MatchIn:
    def __init__(self, obj):
        self.obj = obj

    def __eq__(self, other):
        return self.obj in other

class MatchRe:
    def __init__(self, string):
        self.string = string

    def __eq__(self, other):
        pattern = re.compile(other)
        return pattern.match(self.string) is not None

def last_enumerate(iterable, **kwargs):
    for i, thing in enumerate(iterable, **kwargs):
        at_last = i == len(iterable) - 1
        yield (at_last, thing)

def repr_expand(iterable):
    iterable = [escape_whitespace(obj) for obj in iterable]

    if len(iterable) < 2:
        return repr(iterable[0])

    return ", ".join(iterable[:-1]) + f" or {iterable[-1]}"

def escape_whitespace(string):
    if string == "":
        return "EOF"

    string = string.replace(r"\n", r"\\n").replace(r"\t", r"\\t")
    return re.sub(r"(\t| {4})+", r"\\t", string.replace("\n", r"\n"))

def set_add(items, new_items):
    for item in new_items:
        if item in items:
            continue

        items += [item]

    return items
