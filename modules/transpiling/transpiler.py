class Transpiler:
    def __init__(self, options, filepath):
        self.headers = set()
        self.human_readable = "t" in options
        self.file = open(filepath, "w", encoding = "UTF-8")

    def __del__(self):
        self.file.close()

    def add_header(self, string):
        self.headers.add(string)
