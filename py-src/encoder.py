from filelock import FileLock

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

    @staticmethod
    def encode_action_lists(filename, lists, ticknum):
        file = open(filename + "." + str(ticknum), "w")
        for actions in lists:
            for action in actions:
                file.write(str(action))
        file.close()


def encode_generated_map(filename, coords, start_pos):
    with open(filename, 'w') as f:
        for c in coords[:-1]:
            f.write("("+str(c[0]) + "," + str(c[1])+"),")
        f.write("(" + str(coords[len(coords)-1][0]) + "," + str(coords[len(coords)-1][1]) + ")#")
        f.write(str(start_pos))
        f.write("##")


