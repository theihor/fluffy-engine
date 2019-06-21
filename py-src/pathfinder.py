from constants import Cell


def bfsFind(state, start, endP):
    prev = [row[:] for row in [[None] * state.width]
            * state.height]

    def available(x, y):
        return (x >= 0 and x < state.width
                and y >= 0 and y < state.height
                and state.cell(x, y)[1] is not Cell.OBSTACLE
                and prev[y][x] is None
                and (x != start[0] or y != start[1]))
    front = [start]
    (endX, endY) = (-1, -1)

    def find():
        nonlocal front, endX, endY
        while len(front) != 0:
            # print('Front = ', front)
            newFront = []
            for (x, y) in front:
                for (dx, dy) in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    x1 = x + dx
                    y1 = y + dy
                    if available(x1, y1):
                        # print('avail ', (x1, y1))
                        newFront.append((x1, y1))
                        prev[y1][x1] = (x, y)
                        if endP(x1, y1):
                            (endX, endY) = (x1, y1)
                            return
            front = newFront
    find()
    if endX == -1:
        return None
    (curX, curY) = (endX, endY)
    path = [(endX, endY)]
    while True:
        prevPos = prev[curY][curX]
        if prevPos is None:
            break
        path.append(prevPos)
        (curX, curY) = prevPos
    path.reverse()
    return path
