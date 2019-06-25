class Encoder:
    @staticmethod
    def encodeToFile(filename, state, add_score=True):
        if add_score:
            filename = filename + "." + str(state.tickNum)
        file = open(filename, "w")
        sep = ''
        for actions in state.actions():
            file.write(sep)
            for action in actions:
                file.write(str(action))
            sep = '#'
        file.close()
