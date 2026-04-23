import io


class Image():
    def __init__(self, path: str):
        self.path = path

    def save(self, fd: io.BufferedWriter, format: str):
        assert format.lower() == self.path.split(".")[-1].lower()
        with open(self.path, "rb") as f:
            fd.write(f.read())
