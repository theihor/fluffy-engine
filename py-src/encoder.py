class Encoder:
    @staticmethod
    def encodeToFile(filename, solution: list):
        file = open(filename, "w")
        for sol in solution:
            file.write(str(sol))
        file.close()
