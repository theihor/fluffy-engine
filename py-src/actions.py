class SimpleAction:
    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return self.value


class MoveUp(SimpleAction):
    def __init__(self):
        super().__init__("W")


class MoveDown(SimpleAction):
    def __init__(self):
        super().__init__("S")


class MoveLeft(SimpleAction):
    def __init__(self):
        super().__init__("A")


class MoveRight(SimpleAction):
    def __init__(self):
        super().__init__("D")


class DoNothing(SimpleAction):
    def __init__(self):
        super().__init__("Z")


class TurnRight(SimpleAction):
    def __init__(self):
        super().__init__("E")


class TurnLeft(SimpleAction):
    def __init__(self):
        super().__init__("Q")


class AttachWheels(SimpleAction):
    def __init__(self):
        super().__init__("F")


class AttachDrill(SimpleAction):
    def __init__(self):
        super().__init__("L")


class AttachManipulator:
    def __init__(self, coords: tuple):
        (self.x, self.y) = coords

    def __str__(self):
        return "B({},{})".format(self.x, self.y)
