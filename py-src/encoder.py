class Encoder:
    @staticmethod
    def encodeToFile(filename, state):
        file = open(filename + "." + str(state.tickNum), "w")
        sep = ''
        for actions in state.actions():
            file.write(sep)
            for action in actions:
                file.write(str(action))
            sep = '#'
        file.close()
