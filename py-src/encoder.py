class Encoder:
    @staticmethod
    def encodeToFile(filename, state):
        file = open(filename + "." + str(state.tickNum), "w")
        for actions in state.actions():
            for action in actions:
                file.write(str(action))
        file.close()
