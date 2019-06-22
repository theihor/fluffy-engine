from state import *
from actions import *
import random
import decode
import encoder
import copy
import os
import pickle

qmap = {}

all_actions = [MoveDown(), MoveUp(), MoveLeft(), MoveRight(), TurnLeft(), TurnRight()]

epsilon = 0.005


def state_key(state):
    (bx, by) = state.bots[0].pos
    arr = []
    ms = [(bx + x, by + y) for (x, y) in state.bots[0].manipulators]
    for x in range(bx - 2, bx + 3):
        for y in range(by - 1, by + 3):
            if (x, y) in ms:
                continue
            if 0 <= x < state.width and 0 <= y < state.height:
                (_, c) = state.cell(x, y)
                if c == Cell.ROT:
                    arr.append('r')
                else:
                    arr.append('c') # clean
            else:
                arr.append('o')
    return ''.join(arr)


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


alpha = 0.05 # learning rate
gamma = 0.95  # discount factor


def learning_run1(state, random_start=False):
    action_list = []
    max_steps = state.height * state.width

    if random_start:
        start_pos = None
        while not start_pos or not state.cell(*start_pos)[1] == Cell.CLEAN:
            start_pos = (random.randint(0, state.width -1),
                         random.randint(0, state.height - 1))
    else:
        start_pos = state.botPos()
    steps = 0
    state.setBotPos(*start_pos)
    while not state.is_all_clean() and steps < max_steps:
        (a, v) = q_action(state)
        key = state_key(state) + str(a)
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
        with open(dumped_qmap_name, "rb") as f:
            qmap = pickle.load(f)

    best_sol = learning_run1(get_state(task_id), random_start=False)

    if not best_sol: return

    best_len = len(best_sol)
    for i in range(iterations):
        random_start = random.random() > 0.1
        sol = learning_run1(get_state(task_id), random_start=random_start)
        if i % 10 == 0:
            print(str(i) + ": " + str(best_len))
        if not random_start and best_len > len(sol):
            best_sol = sol
            best_len = len(sol)
    #print(qmap)
    with open(dumped_qmap_name, "wb") as f:
        pickle.dump(qmap, f)
    # with open(dumped_qmap_name, "rb") as f:
    #     qmap1 = pickle.load(f)
    #     for key in qmap:
    #         if qmap[key] != qmap1[key]:
    #             raise RuntimeError("BAD DUMP")
    return best_sol

for i in range(10):
    al = learn("prob-002")
    print("res at i = " + str(i) + ": " + str(len(al)))
    encoder.Encoder.encodeToFile("../test.sol", [al])

