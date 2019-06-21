class SimpleAction:
    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return self.value


class AttachManipulatorAction:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __str__(self):
        return "B({},{})".format(self.x, self.y)
