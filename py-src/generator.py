from constants import Cell
from decode import parse_puzzle
from state import *

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
    for x in range(size):
        cells[0][x] = o
        cells[size-1][x] = o
    for y in range(size):
        cells[y][0] = o
        cells[y][size-1] = o

    # draw a line to frame from every 'obstacle'
    def fill_to_frame(x, y, dx=0, dy=0):
        if dx != 0:
            while 0 <= x < size - 1:
                #print("cells[" + str(y) + "][" + str(x) + "]")
                cells[y][x] = o
                x += dx
        elif dy != 0:
            while 0 <= y < size - 1:
                cells[y][x] = o
                y += dy

    for (x, y) in c['oSqs']:

        # trying go right
        can_go = True
        for dx in range(size-x-1):
            if (x + dx, y) in c['iSqs']:
                can_go = False
                break
        if can_go:
            print("fillin from " + str((x, y)))
            fill_to_frame(x, y, dx = 1)
        else:
            can_go = True
            # try left
            for dx in range(x):
                if (x - dx, y) in c['iSqs']:
                    can_go = False
                    break
            if can_go: fill_to_frame(x, y, dx=-1)
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
                    if can_go: fill_to_frame(x, y, dy=-1)
                    else: raise RuntimeError("Need maneur :(")
    print_cells(cells, size, size)