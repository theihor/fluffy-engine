import pathfinder
from constants import Direction
from solver import moveCommand
from actions import *
import random
import decode
import encoder
import copy
import os
import pickle
from filelock import FileLock
import sys


class GoToClosestRot(SimpleAction):
    def __init__(self):
        super().__init__("G")

    def validate(self, state: State, bot):
        return True

    def process(self, state: State, bot):
        super().process(state, bot)



qmap = {}

all_actions = [MoveDown(), MoveUp(), MoveLeft(), MoveRight(), TurnLeft(), TurnRight(), GoToClosestRot()]

epsilon = 0.001
alpha = 0.01 # learning rate
gamma = 0.95  # discount factor


def state_key(state):
    bot = state.bots[0]
    (bx, by) = bot.pos
    arr = []
    ms = [(bx + x, by + y) for (x, y) in bot.manipulators] + [(bx, by)]

    xl = []; yl = []
    outer_x = True
    if bot.direction == Direction.RIGHT:
        xl = list(range(bx - 1, bx + 3))
        xl.reverse()
        yl = list(range(by - 2, by + 3))
        yl.reverse()
        outer_x = True
    elif bot.direction == Direction.DOWN:
        xl = list(range(bx - 2, bx + 3))
        xl.reverse()
        yl = list(range(by - 1, by + 3))
        outer_x = False
    elif bot.direction == Direction.LEFT:
        xl = list(range(bx - 1, bx + 3))
        yl = list(range(by - 2, by + 3))
        outer_x = True
    else:
        xl = list(range(bx - 2, bx + 3))
        yl = list(range(by - 1, by + 3))
        yl.reverse()
        outer_x = False

    def process_p(x, y):
        if 0 <= x < state.width and 0 <= y < state.height:
            (_, c) = state.cell(x, y)
            if c == Cell.ROT:
                arr.append('r')
            else:
                arr.append('c')  # clean
        else:
            arr.append('o')

    if outer_x:
        for x in xl:
            for y in yl:
                if not (x, y) in ms: process_p(x, y)
    else:
        for y in yl:
            for x in xl:
                if not (x, y) in ms: process_p(x, y)

    key = ''.join(arr)
    if len(xl) * len(yl) != 20:
        print(str(len(xl)) + " x " + str(len(yl)))
        print(key)
    return key


def q_action(state):
    valid_actions = [a for a in all_actions if a.validate(state, state.bots[0])]
    def value(a):
        key = state_key(state) + str(a)
        if not key in qmap:
            qmap[key] = random.random() * 1e-5
        return qmap[key]
    if random.random() < epsilon:
        a = random.choice(valid_actions)
        return (a, value(a))
    else:
        best = valid_actions[0]
        bestv = value(best)
        for a in valid_actions[1:]:
            v = value(a)
            if v > bestv:
                bestv = v
                best = a
        return (best, bestv)




def learning_run1(state, random_start=False):
    action_list = []
    max_steps = state.height * state.width * 3

    if random_start:
        start_pos = None
        while not start_pos or not state.cell(*start_pos)[1] == Cell.CLEAN:
            start_pos = (random.randint(0, state.width -1),
                         random.randint(0, state.height - 1))
    else:
        start_pos = state.botPos()
    steps = 0
    state.setBotPos(*start_pos)
    path = pathfinder.bfsFind(state, state.bots[0].pos, lambda l, x, y: state.cell(x, y)[1] == Cell.ROT)
    while path and steps < max_steps:
        (a, v) = q_action(state)
        key = state_key(state) + str(a)
        r = 0
        if isinstance(a, GoToClosestRot):
            if path:
                commands = []
                for (pos, nextPos) in zip(path, path[1:]):
                    commands.append(moveCommand(pos, nextPos))
                # print(commands)
                for c in commands:
                    action_list.append(c)
                    state.nextAction(c)
                    steps += 1
                    r -= 1
                    r += state.last_painted
        else:
            action_list.append(a)
            state.nextAction(a)
            steps += 1

        if state.last_painted > 0:
            r = state.last_painted
        else: r = -1

        # update Q

        (_, v1) = q_action(state)
        #print("r = " + str(r) + ", q = " + str(qmap[key]), end=" ")
        qmap[key] += alpha * (r + gamma * v1 - v)
        #print("q1 = " + str(qmap[key]))

        path = pathfinder.bfsFind(state, state.bots[0].pos, lambda l, x, y: state.cell(x, y)[1] == Cell.ROT)

    if random_start: return False
    else: return action_list

iterations = 100

state = None
id = None


def get_state(task_id):
    global state, id
    if not state:
        filename = "../desc/" + task_id + ".desc"
        print(filename)
        state = State.decode(decode.parse_task(filename))
        id = task_id
        return copy.deepcopy(state)
    elif id == task_id:
        return copy.deepcopy(state)
    else:
        state = None
        return get_state(task_id)


def learn(task_id):
    global qmap

    dumped_qmap_name = "../qmaps/main_qmap.pickle"

    if os.path.isfile(dumped_qmap_name):
        with FileLock("../qmaps/.lock"):
            with open(dumped_qmap_name, 'rb') as f:
                qmap = pickle.load(f)

    best_sol = learning_run1(get_state(task_id), random_start=False)

    if not best_sol: return

    best_len = len(best_sol)
    for i in range(iterations):
        random_start = False
        sol = learning_run1(get_state(task_id), random_start=random_start)
        if i % 10 == 0:
            print(str(i) + ": " + str(best_len))
        if not random_start and best_len >= len(sol):
            best_sol = sol
            best_len = len(sol)
    #print(qmap)
    with FileLock("../qmaps/.lock"):
        with open(dumped_qmap_name, "wb") as f:
            pickle.dump(qmap, f)
    # with open(dumped_qmap_name, "rb") as f:
    #     qmap1 = pickle.load(f)
    #     for key in qmap:
    #         if qmap[key] != qmap1[key]:
    #             raise RuntimeError("BAD DUMP")
    return best_sol

args = sys.argv[1:]

if args and len(args) >= 2:
    k1 = int(args[0])
    k2 = int(args[1])

    for i in range(k1, k2):
        task_id = "prob-"
        if i < 10: task_id += "00" + str(i)
        elif i < 100: task_id += "0" + str(i)
        else: task_id += str(i)
        al = learn(task_id)
        print("res for " + str(task_id) + ": " + str(len(al)))
        encoder.Encoder.encodeToFile("../q-sol/" + task_id + "-" + str(len(al)) + ".sol", [al])

