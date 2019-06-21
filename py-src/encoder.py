class Encoder:
    @staticmethod
    def encode(task_no: int, solution: list):
        file = open("prob-{:03d}.sol".format(task_no), "w")
        for sol in solution:
            file.write(str(sol))
        file.close()
