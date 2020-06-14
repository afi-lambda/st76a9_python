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
                if chunk == '':
                    raise StopIteration
                else:
                    return chunk.rstrip()
            if line.isspace():
                return chunk.rstrip()
            else:
                chunk += line
