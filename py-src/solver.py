from state import State, Cell
import decode
from encoder import Encoder
from actions import MoveUp, MoveDown, MoveLeft, MoveRight
import pathfinder


def solve(taskFile, solutionFile, solver):
    st = State.decode(decode.parse_task(taskFile))
    commands = solver(st)
    Encoder.encodeToFile(solutionFile, commands)


def moveCommand(posFrom, posTo):
    (xf, yf) = posFrom
    (xt, yt) = posTo
    if xt == xf:
        if yt < yf:
            return MoveDown()
        else:
            return MoveUp()
    if xt < xf:
        return MoveLeft()
    else:
        return MoveRight()


def pathToCommands(path):
    commands = []
    for (pos, nextPos) in zip(path, path[1:]):
        commands.append(moveCommand(pos, nextPos))
    return commands


def closestRotSolver(st):
    while True:
        path = pathfinder.bfsFind(st, st.botPos(),
                                  lambda x, y: st.cell(x, y)[1] == Cell.ROT)
        if path is None:
            break
        commands = pathToCommands(path)
        for command in commands:
            st.nextAction(command)
    return st.actions
