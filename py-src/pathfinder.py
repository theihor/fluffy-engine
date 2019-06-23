from constants import Cell


def bfsFind(state, start, endP, availP=None,
            register=lambda l, x, y: None,
            max_path_len=None):
    prev = [row[:] for row in [[None] * state.width]
            * state.height]
    if availP is None:
        availP = lambda l, x, y: state.cell(x, y)[1] is not Cell.OBSTACLE

    def available(l, x, y):
        return (0 <= x < state.width
                and 0 <= y < state.height
                and prev[y][x] is None
                and availP(l, x, y)
                and (x != start[0] or y != start[1]))

    front = [start]
    (endX, endY) = (-1, -1)

    def find():
        nonlocal front, endX, endY
        pathLen = 1
        while len(front) != 0:
            # print('Front = ', front)
            newFront = []
            for (x, y) in front:
                for (dx, dy) in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    x1 = x + dx
                    y1 = y + dy
                    if available(pathLen, x1, y1):
                        # print('avail ', (x1, y1))
                        newFront.append((x1, y1))
                        prev[y1][x1] = (x, y)
                        register(pathLen, x1, y1)
                        if endP(pathLen, x1, y1):
                            (endX, endY) = (x1, y1)
                            return
            front = newFront
            pathLen += 1
            if max_path_len is not None and pathLen > max_path_len:
                return

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


def bfsFindClosest(state, start, endP, availP=lambda x, y: True,
                   rank=lambda x, y: 1,
                   max_path_len=None):
    prev = [row[:] for row in [[None] * state.width]
            * state.height]

    def available(x, y):
        return (x >= 0 and x < state.width
                and y >= 0 and y < state.height
                and state.cell(x, y)[1] is not Cell.OBSTACLE
                and prev[y][x] is None
                and availP(x, y)
                and (x != start[0] or y != start[1]))

    front = [start]
    pathLen = 1
    found = []
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
                    if endP(pathLen, x1, y1):
                        found.append((x1, y1))
        front = newFront
        pathLen += 1
        if max_path_len is not None and pathLen > max_path_len:
            break
        if max_path_len is None and len(found) > 0:
            break
    if len(found) == 0:
        return None
    ranked = map(lambda p: (rank(p[0], p[1]), p), found)
    (bestRank, (endX, endY)) = min(ranked, key=lambda x: x[0])
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


def blobSplit(state, blobSize):
    filled = [row[:] for row in [[False] * state.width]
              * state.height]
    blobs = []

    def anyRot():
        for y in range(state.height):
            for x in range(state.width):
                if (state.cell(x, y)[1] is Cell.ROT and not filled[y][x]):
                    return (x, y)
        return None

    while True:
        start = anyRot()
        if start is None:
            break
        blob = {start}
        filled[start[1]][start[0]] = True

        def registerCell(l, x, y):
            filled[y][x] = True
            blob.add((x, y))

        bfsFind(state, start,
                endP=lambda l, x, y: len(blob) >= blobSize,
                availP=lambda l, x, y: not filled[y][x],
                register=registerCell)
        blobs.append(blob)
    return blobs
