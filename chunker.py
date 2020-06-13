class Chunker:
    def __init__(self, file):
        self.file = file

    def __iter__(self):
        return self

    def __next__(self):
        chunk = ''
        while True:
            line = self.file.readline()
            if line == '':
                raise StopIteration
            if line.isspace():
                return chunk.rstrip()
            else:
                chunk += line
