from state import *
from actions import *
import random
import decode
import encoder
import copy

qmap = {}

all_actions = [MoveDown(), MoveUp(), MoveLeft(), MoveRight(), TurnLeft(), TurnRight()]

epsilon = 0.01

def q_action(state):
    bpos = state.botPos()
    valid_actions = [a for a in all_actions if a.validate(state)]
    def value(a):
        key = (bpos, str(a))
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

alpha = 0.02 # learning rate
gamma = 0.9  # discount factor


def learning_run1(state):
    action_list = []
    while not state.is_all_clean():
        (a, v) = q_action(state)
        bpos1 = state.botPos()
        action_list.append(a)
        state.nextAction(a)
        bpos2 = state.botPos()
        r = state.last_painted - 1

        # update Q
        key = (bpos1, str(a))
        (_, v1) = q_action(state)
        qmap[key] += alpha * (r + gamma * v1 - v)

    return action_list

iterations = 1000

def learn(state):
    best_sol = learning_run1(copy.deepcopy(state))
    best_len = len(best_sol)
    for i in range(iterations):
        sol = learning_run1(copy.deepcopy(state))
        if i % 100 == 0:
            print(str(i) + ": " + str(best_len))
        if best_len > len(sol):
            best_sol = sol
            best_len = len(sol)
    print(qmap)
    return best_sol

s = State.decode(decode.parse_task("../desc/prob-020.desc"))
al = learn(s)
encoder.Encoder.encodeToFile("../test.sol", al)
