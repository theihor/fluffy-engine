from constants import Cell, Direction
from decode import parse_puzzle, parse_task
import random
from state import *
from encoder import *


def constraints_from_parsed(parsed_puzzle):
    (coefs, isqs, osqs) = parsed_puzzle
    c = {}
    #puzzle::=bNum,eNum,tSize,vMin,vMax,mNum,fNum,dNum,rNum,cNum,xNum#iSqs#oSqs
    c["bNum"] = coefs[0]
    c["eNum"] = coefs[1]
    c["tSize"] = coefs[2]
    c["vMin"] = coefs[3]
    c["vMax"] = coefs[4]
    c["mNum"] = coefs[5]
    c["fNum"] = coefs[6]
    c["dNum"] = coefs[7]
    c["rNum"] = coefs[8]
    c["cNum"] = coefs[9]
    c["xNum"] = coefs[10]
    c["iSqs"] = isqs
    c["oSqs"] = osqs
    return c


def generate(c):
    o = (None, Cell.OBSTACLE)
    size = round(c['tSize'] * 1)
    cells = [row[:] for row in [[(None, Cell.ROT)] * size] * size]
    print("size = " + str(len(cells)) + " x " + str(len(cells[0])))
    # make a frame
    # for x in range(size):
    #     cells[0][x] = o
    #     cells[size-1][x] = o
    # for y in range(size):
    #     cells[y][0] = o
    #     cells[y][size-1] = o

    # draw a line to frame from every 'obstacle'
    def fill_to_frame(x, y, dx=0, dy=0):
        if dx != 0:
            while 0 <= x < size - 1 and cells[y][x][1] == Cell.ROT:
                #print("cells[" + str(y) + "][" + str(x) + "]")
                cells[y][x] = o
                x += dx
        elif dy != 0:
            while 0 <= y < size - 1 and cells[y][x][1] == Cell.ROT:
                cells[y][x] = o
                y += dy

    def draw_from_o(x, y):
        # trying go right
        can_go = True
        for dx in range(size - x - 1):
            if (x + dx, y) in c['iSqs']:
                can_go = False
                break
        if can_go:
            print("fillin from " + str((x, y)))
            fill_to_frame(x, y, dx=1)
        else:
            can_go = True
            # try left
            for dx in range(x):
                if (x - dx, y) in c['iSqs']:
                    can_go = False
                    break
            if can_go:
                fill_to_frame(x, y, dx=-1)
            else:
                can_go = True
                # try up
                for dy in range(size - y - 1):
                    if (x, y + dy) in c['iSqs']:
                        can_go = False
                        break
                    if can_go: fill_to_frame(x, y, dy=1)
                else:
                    can_go = True
                    # try down
                    for dy in range(y):
                        if (x, y - dy) in c['iSqs']:
                            can_go = False
                            break
                    if can_go:
                        fill_to_frame(x, y, dy=-1)
                    else:
                        raise RuntimeError("Need maneur :(")

    # print_cells(cells, size, size)

    for (x, y) in c['oSqs']: draw_from_o(x, y)
        # # trying go right
        # can_go = True
        # for dx in range(size-x-1):
        #     if (x + dx, y) in c['iSqs']:
        #         can_go = False
        #         break
        # if can_go:
        #     print("fillin from " + str((x, y)))
        #     fill_to_frame(x, y, dx = 1)
        # else:
        #     can_go = True
        #     # try left
        #     for dx in range(x):
        #         if (x - dx, y) in c['iSqs']:
        #             can_go = False
        #             break
        #     if can_go: fill_to_frame(x, y, dx=-1)
        #     else:
        #         can_go = True
        #         # try up
        #         for dy in range(size - y - 1):
        #             if (x, y + dy) in c['iSqs']:
        #                 can_go = False
        #                 break
        #             if can_go: fill_to_frame(x, y, dy=1)
        #         else:
        #             can_go = True
        #             # try down
        #             for dy in range(y):
        #                 if (x, y - dy) in c['iSqs']:
        #                     can_go = False
        #                     break
        #             if can_go: fill_to_frame(x, y, dy=-1)
        #             else: raise RuntimeError("Need maneur :(")
    #print_cells(cells, size, size)

    coords = cells_to_polygon(cells, size, size)


    while len(coords) < c['vMin']:
        print("Not enough vertices: " + str(len(coords)))
        n = round(c['vMin'] - len(coords) / 4)
        i = 0
        while i < len(coords) - 1:
            (x1, y1) = coords[i]
            (x2, y2) = coords[i+1]

            if x1 == x2 and abs(y2 - y1) >= 3:
                if y1 < y2: # up
                    allowed_to_fill = True
                    for y in range(y1, y1 + 3):
                        for x in range(x1 - 2, x1):
                            if (x, y) in c['iSqs'] or cells[y][x][1] == Cell.OBSTACLE:
                                allowed_to_fill = False
                                break
                    if allowed_to_fill:
                        cells[y1 + 1][x1 - 1] = o
                else: # down
                    allowed_to_fill = True
                    for y in range(y2, y2 + 3):
                        for x in range(x1 - 2, x1):
                            if (x, y) in c['iSqs'] or cells[y][x][1] == Cell.OBSTACLE:
                                allowed_to_fill = False
                                break
                    if allowed_to_fill:
                        cells[y2 + 1][x1 + 1] = o
            elif y1 == y2 and abs(x2 - x1) >= 3:
                if x1 < x2: # right
                    allowed_to_fill = True
                    for x in range(x1, x1 + 3):
                        for y in range(y1, y1 + 2):
                            if (x, y) in c['iSqs'] or cells[y][x][1] == Cell.OBSTACLE:
                                allowed_to_fill = False
                                break
                    if allowed_to_fill:
                        cells[y1 + 1][x1 + 1] = o
                # else: # down
                #     allowed_to_fill = True
                #     for y in range(y2, y2 + 3):
                #         for x in range(x1 - 2, x1):
                #             if (x, y) in c['iSqs'] or cells[y][x][1] == Cell.OBSTACLE:
                #                 allowed_to_fill = False
                #                 break
                #     if allowed_to_fill:
                #         cells[y2 + 1][x1 - 1] = o
            i += 1

        coords = cells_to_polygon(cells, size, size)

    if c['iSqs']:
        start_pos = random.choice(c['iSqs'])
    else: start_pos = (0, 0)
    return cells, size, start_pos


def left_of(d):
    return {Direction.RIGHT: Direction.UP,
            Direction.UP: Direction.LEFT,
            Direction.LEFT: Direction.DOWN,
            Direction.DOWN: Direction.RIGHT}[d]


def right_of(d):
    return {Direction.RIGHT: Direction.DOWN,
            Direction.DOWN: Direction.LEFT,
            Direction.LEFT: Direction.UP,
            Direction.UP: Direction.RIGHT}[d]


def cells_to_polygon(cells, width, height):
    face = Direction.RIGHT
    points = [(0, 0)]
    x = 0; y = 0
    moved = False

    def is_o(dx, dy):
        x1 = x + dx
        y1 = y + dy
        if 0 <= x1 < width and 0 <= y1 < height:
            return cells[y1][x1][1] == Cell.OBSTACLE
        else: return True

    def step_d(face_):
        return {Direction.RIGHT: (1, 0),
                Direction.UP: (0, 1),
                Direction.LEFT: (-1, 0),
                Direction.DOWN: (0, -1)
                }[face_]

    def move(move_direction):
        # move_direction is LEFT, RIGHT or UP (meaning FORWARD)
        if move_direction == Direction.RIGHT:
            return step_d(right_of(face)), right_of(face)
        elif move_direction == Direction.LEFT:
            return step_d(left_of(face)), left_of(face)
        elif move_direction == Direction.UP:
            return step_d(face), face
        else:
            raise RuntimeError("SHould never be here")

    while True:
        #print(str(x) + " " + str(y))
        # check if obstacle is right from us
        ((dx, dy), new_face) = move(Direction.RIGHT)
        if is_o(dx, dy):
            #print("obstacle right from us, check forward")

            ((dx, dy), new_face) = move(Direction.UP)
            if is_o(dx, dy):
                #print( "obstacle in front of us and right from us, turn left")
                (_, new_face) = move(Direction.LEFT)
                if new_face != face:
                    if face == Direction.RIGHT:
                        points.append((x + 1, y))
                    elif face == Direction.DOWN:
                        points.append((x, y))
                    elif face == Direction.LEFT:
                        points.append((x, y + 1))
                    elif face == Direction.UP:
                        points.append((x + 1, y + 1))
                    face = new_face
                else:
                    raise RuntimeError("This should never happen")
                pass
            else:
                #print(" no obstacle in front, go forward")
                x += dx; y += dy
                moved = True

        else:
            #print("no obstacle right from us, turn right and go there")
            # no obstacle right from us,
            # turn right and go there
            if new_face != face:
                if face == Direction.RIGHT:
                    points.append((x, y))
                elif face == Direction.DOWN:
                    points.append((x, y + 1))
                elif face == Direction.LEFT:
                    points.append((x + 1, y + 1))
                elif face == Direction.UP:
                    points.append((x + 1, y))
                face = new_face
            else:
                raise RuntimeError("This should never happen")
            x += dx; y += dy
            moved = True

        if moved and x == 0 and y == 0: break
    return points

#state = State.decode(parse_task("../examples/example-01.desc"))
#state.show()
#print(cells_to_polygon(state.cells, state.width, state.height))


def generate_and_dump(puzzle):
    cells, size, start_pos = generate(puzzle)
    coords = cells_to_polygon(cells, size, size)
    encode_generated_map("../map.desc", coords, start_pos)

p = parse_puzzle("../puzzles/puzzle20-56.cond")
generate_and_dump(constraints_from_parsed(p))

