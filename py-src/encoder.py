class Encoder:
    @staticmethod
    def encodeToFile(filename, state):
        file = open(filename + "." + str(state.tickNum), "w")
        for actions in state.actions():
            for action in actions:
                file.write(str(action))
        file.close()


def encode_generated_map(filename, coords, start_pos, boosters):
    with open(filename, 'w') as f:
        for c in coords[:-1]:
            f.write("("+str(c[0]) + "," + str(c[1])+"),")
        f.write("(" + str(coords[len(coords)-1][0]) + "," + str(coords[len(coords)-1][1]) + ")#")
        f.write("("+str(start_pos[0]) + "," + str(start_pos[1])+")")
        f.write("##")
        sep = ''
        for (code, (x, y)) in boosters:
            f.write("{}{}({},{})".format(sep, code, x, y))
            sep = ';'
