class Encoder:
    @staticmethod
    def encodeToFile(filename, solution: list):
        file = open(filename, "w")
        for actions in solution:
            for action in actions:
                file.write(str(action))
        file.close()
