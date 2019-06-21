class Encoder:
    @staticmethod
    def encode(task_no: int, solution: list):
        Encoder.encodeToFile("prob-{:03d}.sol", solution)

    @staticmethod
    def encodeToFile(filename, solution: list):
        file = open(filename, "w")
        for sol in solution:
            file.write(str(sol))
        file.close()
