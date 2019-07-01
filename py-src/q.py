import math

import pathfinder
from constants import *
from predicates import drillableP, boosterP
from actions import *
import random
import decode
import encoder
import copy
import os
import pickle
import sys

import numpy as np
import tensorflow as tf
from tensorflow import keras

class GoToClosestRot(SimpleAction):
    def __init__(self):
        super().__init__("GR")

    def validate(self, state: State, bot):
        return True

    def process(self, state: State, bot):
        super().process(state, bot)

class GoToBooster(SimpleAction):
    def __init__(self):
        super().__init__("GB")

    def validate(self, state: State, bot):
        return True

    def process(self, state: State, bot):
        super().process(state, bot)



class ShiftRandom(Shift):
    def __init__(self):
        self.pos = None

    def validate(self, state: State, bot):
        return len(state.pods) > 0

    def process(self, state: State, bot):
        self.pos = random.choice(list(state.pods))
        super().process(state, bot)

    def __str__(self):
        return "T"


constant_actions = [
    MoveDown(),  # meaning BACKWARD
    MoveUp(),    # meaning FORWARD
    MoveLeft(),  # relative to face
    MoveRight(), # relative to face
    TurnLeft(),
    TurnRight(),
    #GoToClosestRot(),
    #AttachDrill(),
    #AttachWheels(),
    #Reset(),
    #ShiftRandom()
]


def all_actions(bot):
    #lst = constant_actions.copy()
    #lst.append(AttachManipulator(SimpleAttacher().get_position(bot)))
    #lst.append(AttachManipulator(ExperimentalAttacher(forward).get_position(bot)))
    #lst.append(AttachManipulator(ExperimentalAttacher(forward_wide).get_position(bot)))
    #lst.append(AttachManipulator(ExperimentalAttacher(experimental).get_position(bot)))
    #lst.append(AttachManipulator(ExperimentalAttacher(long_center).get_position(bot)))
    #lst.append(AttachManipulator(ExperimentalAttacher(long_left).get_position(bot)))
    #lst.append(AttachManipulator(ExperimentalAttacher(long_right).get_position(bot)))

    return constant_actions


epsilon = 0.01
alpha = 0.01 # learning rate
gamma = 0.9  # discount factor

def init_q_value():
    return random.random() * 1e-1

local_visibility_map = {
            (-3, -3): [(-2, -2), (-1, -1)],
            (-3, +3): [(-2, +2), (-1, +1)],
            (+3, -3): [(+2, -2), (+1, -1)],
            (+3, +3): [(+2, +2), (+1, +1)],

            (-2, -2): [(-1, -1)],
            (-2, +2): [(-1, +1)],
            (+2, -2): [(+1, -1)],
            (+2, +2): [(+1, +1)],

            (-1, -1): [],
            (-1, +1): [],
            (+1, -1): [],
            (+1, +1): [],

            (+0, +1): [],
            (+0, -1): [],
            (+1, +0): [],
            (-1, +0): [],

            (+0, +2): [(+0, +1)],
            (+0, -2): [(+0, -1)],
            (+2, +0): [(+1, +0)],
            (-2, +0): [(-1, +0)],

            (+0, +3): [(+0, +1), (+0, +2)],
            (+0, -3): [(+0, -1), (+0, -2)],
            (+3, +0): [(+1, +0), (+2, +0)],
            (-3, +0): [(-1, +0), (-2, +0)],

            (-3, +2): [(-2, +2), (-2, +1), (-1, +1), (-1, 0)],
            (-3, -2): [(-2, -2), (-2, -1), (-1, -1), (-1, 0)],
            (+3, +2): [(+2, +2), (+2, +1), (+1, +1), (+1, 0)],
            (+3, -2): [(+2, -2), (+2, -1), (+1, -1), (+1, 0)],

            (-2, +3): [(-2, +2), (-1, +2), (-1, +1), (0, +1)],
            (-2, -3): [(-2, -2), (-1, -2), (-1, -1), (0, -1)],
            (+2, +3): [(+2, +2), (+1, +2), (+1, +1), (0, +1)],
            (+2, -3): [(+2, -2), (+1, -2), (+1, -1), (0, -1)],

            (-1, -3): [(-1, -2), (0, -1)],
            (+1, -3): [(+1, -2), (0, -1)],
            (-1, +3): [(-1, +2), (0, +1)],
            (+1, +3): [(+1, +2), (0, +1)],

            (-3, -1): [(-2, -1), (-1, 0)],
            (+3, -1): [(+2, -1), (+1, 0)],
            (-3, +1): [(-2, +1), (-1, 0)],
            (+3, +1): [(+2, +1), (+1, 0)],

            (-1, -2): [(-1, -1), (0, -1)],
            (+1, -2): [(+1, -1), (0, -1)],
            (-1, +2): [(-1, +1), (0, +1)],
            (+1, +2): [(+1, +1), (0, +1)],

            (-2, -1): [(-1, -1), (-1, 0)],
            (+2, -1): [(+1, -1), (+1, 0)],
            (-2, +1): [(-1, +1), (-1, 0)],
            (+2, +1): [(+1, +1), (+1, 0)],

            (0, 0): [],
}

# as if bot looks up
vision_range_x = range(-3, +4)
vision_range_y = range(-3, +4)

traverse_list = {
    Direction.RIGHT: (list(reversed(vision_range_x)),
                      list(reversed(vision_range_y)),
                      True),
    Direction.DOWN:  (list(reversed(vision_range_x)),
                      list(vision_range_y),
                      False),
    Direction.LEFT: (list(vision_range_x),
                     list(vision_range_y),
                     True),
    Direction.UP: (list(vision_range_x),
                   list(reversed(vision_range_y)),
                   False)
}


def is_locally_visible(state, pos, d):
    (bx, by) = pos
    (dx, dy) = d
    #print("is_locally_visible", d)
    x, y = bx + dx, by + dy
    if (x < 0
        or x >= state.width
        or y < 0
        or y >= state.height
        or state.cell(x, y)[1] == Cell.OBSTACLE):
        return False

    if d in local_visibility_map:
        to_check = local_visibility_map[d]
        for (dx, dy) in to_check:
            x1, y1 = bx + dx, by + dy
            if 0 <= x1 < state.width and 0 <= y1 < state.height:
                (_, c) = state.cell(x1, y1)
                if c == Cell.OBSTACLE:
                    return False
            else:
                return False
        return True
    else:
        raise RuntimeError("Local visibility works only in range 3")

boosters = [
    Booster.WHEEL,
    Booster.MANIPULATOR,
    # Booster.TELEPORT,
    Booster.DRILL,
    # Booster.CLONE,
    # Booster.MYSTERIOUS,
]
priority_boosters = [Booster.MANIPULATOR]

def state_key(state):
    """bot sees cells relative to itself"""
    bot = state.bots[0]
    (bx, by) = bot.pos
    arr = []
    ms = [(bx + x, by + y) for (x, y) in bot.manipulators] + [(bx, by)]

    (xds, yds, outer_x) = traverse_list[bot.direction]
    xl = [bx + dx for dx in xds]
    yl = [by + dy for dy in yds]

    # if bot.direction == Direction.RIGHT:
    #     xl = list(range(bx - 3, bx + 4))
    #     xl.reverse()
    #     yl = list(range(by - 3, by + 4))
    #     yl.reverse()
    #     outer_x = True
    # elif bot.direction == Direction.DOWN:
    #     xl = list(range(bx - 3, bx + 4))
    #     xl.reverse()
    #     yl = list(range(by - 3, by + 4))
    #     outer_x = False
    # elif bot.direction == Direction.LEFT:
    #     xl = list(range(bx - 3, bx + 4))
    #     yl = list(range(by - 3, by + 4))
    #     outer_x = True
    # else:
    #     xl = list(range(bx - 3, bx + 4))
    #     yl = list(range(by - 3, by + 4))
    #     yl.reverse()
    #     outer_x = False

    def is_visible(x, y):
        if (x - bx, y - by) in local_visibility_map:
            to_check = local_visibility_map[(x - bx, y - by)]
            #print(to_check)
            for (dx, dy) in to_check:
                x1, y1 = bx + dx, by + dy
                if 0 <= x1 < state.width and 0 <= y1 < state.height:
                    #print(x1, y1)
                    (_, c) = state.cell(x1, y1)
                    if c == Cell.OBSTACLE:
                        return False
                else:
                    return False
            return True
        else: return state.visible((x, y))

    def process_p(x, y):
        if 0 <= x < state.width and 0 <= y < state.height:
            (booster, c) = state.cell(x, y)

            if c == Cell.OBSTACLE:
                arr.append('o')
                return

            if not is_visible(x, y):
                arr.append('i')
                return

            if (x, y) in ms:
                arr.append('m')
                return

            # if booster in boosters:
            #     if is_visible(x, y): arr.append('b')
            #     else: arr.append('i')
            #     return

            if c == Cell.ROT:
                arr.append('r')
            elif c == Cell.CLEAN:
                arr.append('c')
            else:
                raise RuntimeError('Unexpected Cell')
        else:
            arr.append('o')
    #print(xl, yl)
    if outer_x:
        for x in xl:
            #if arr: print(''.join(arr[-len(yl):]))
            for y in yl:
                process_p(x, y)
    else:
        for y in yl:
            #if arr: print(''.join(arr[-len(xl):]))
            for x in xl:
                process_p(x, y)
    #print()
    key = ''.join(arr)
    # if len(xl) * len(yl) != 49:
    #     print(str(len(xl)) + " x " + str(len(yl)))
    #     print(key)
    return key


cell_states = ['r', 'c', 'o', 'i', 'm']

pair_i = {}
_i = 0
for c1 in ['r', 'c', 'o', 'i', 'm']:
    for c2 in ['r', 'c', 'o', 'i', 'm']:
        pair_i[c1 + c2] = _i
        _i += 1

def state_key_to_bitarray(key):
    # neighbors
    def one_of(i, n):
        a = [0] * n
        a[i] = 1
        return a
    #
    # bits = []
    # for i in range(len(key)):
    #     for di in [-7, -1, +1, +7]:
    #         if 0 <= i + di < len(key):
    #             pair = key[i] + key[i + di]
    #             bits += one_of(pair_i[pair], len(pair_i))


    # independent cells
    pos_of = {
        'r': 0,
        'c': 1,
        'o': 2,
        'i': 3,
        'm': 4
    }
    bits = []
    for c in key:
        arr = [0] * len(pos_of)
        if c != 'b':
            arr[pos_of[c]] = 1
        bits += arr

    # bits = []
    # for i in range(len(key)):
    #     for j in range(len(key)):
    #         if i == j:
    #             continue
    #         if key[i] == 'm':
    #             if key[j] == 'r':
    #                 bits += one_of(0, 4)
    #             else:
    #                 bits += one_of(1, 4)
    #         elif key[j] == 'm':
    #             if key[j] == 'r':
    #                 bits += one_of(2, 4)
    #             else:
    #                 bits += one_of(3, 4)
    #         else:
    #             bits += [0] * 4

    return bits


def get_key(state, bot, action, s_key=None):
    boosters = []
    if bot.drill_duration > 0:
        boosters.append('D')
    else:
        boosters.append('d')

    if bot.wheel_duration > 0:
        boosters.append('W')
    else:
        boosters.append('w')
    if isinstance(action, AttachDrill) or\
            isinstance(action, AttachManipulator) or \
            isinstance(action, AttachWheels):
        return ''.join(boosters) + str(action)
    else:
        if s_key is None: s_key = state_key(state)
        return ''.join(boosters) + s_key + str(action)


def get_state_x(state, bot, s_key=None):
    x = []
    # drill
    if bot.drill_duration > 0: x.append(1)
    else: x.append(0)
    # wheel
    if bot.wheel_duration > 0: x.append(1)
    else: x.append(0)
    # state
    if s_key is None: s_key = state_key(state)
    x += state_key_to_bitarray(s_key)

    return np.vstack([np.array(x, dtype=float)])


def q_value(state, bot, action, s_key=None):
    global qmap
    key = get_key(state, bot, action, s_key=s_key)
    if key not in qmap:
        return init_q_value(), key
    else:
        return qmap[key], key


def q_action(state, bot, s_key=None):
    global qmap
    valid_actions = [a for a in all_actions(bot) if translate_move(bot, a).validate(state, bot)]
    if random.random() < epsilon:
        a = random.choice(valid_actions)
        (v, key) = q_value(state, bot, a, s_key=s_key)
        return translate_move(bot, a), v, key
    else:
        best = valid_actions[0]
        (bestv, best_key) = q_value(state, bot, best, s_key=s_key)
        for a in valid_actions[1:]:
            (v, key) = q_value(state, bot, a, s_key=s_key)
            if v > bestv:
                bestv = v
                best = a
                best_key = key
        return translate_move(bot, best), bestv, best_key


def q_action_linear(state, bot, s_key=None):

    x = get_state_x(state, bot, s_key=s_key)

    pos_of = {
        'W': 0,
        'A': 1,
        'S': 2,
        'D': 3,
        'Q': 4,
        'E': 5,
    }

    def one_of(i, n):
        a = [0] * n
        a[i] = 1
        return np.array(a)

    global qmap
    def q(a):
        w = qmap["w"]
        x_a = np.append(x, one_of(pos_of[str(a)], len(pos_of)))
        return x_a.dot(w), x_a

    valid_actions = [a for a in all_actions(bot) if translate_move(bot, a).validate(state, bot)]
    if random.random() < epsilon:
        a = random.choice(valid_actions)
        (v, x_a) = q(a)
        return translate_move(bot, a), v, x_a
    else:
        best = valid_actions[0]
        (best_v, best_x) = q(best)
        for a in valid_actions[1:]:
            (v, x_a) = q(a)
            if v > best_v:
                best_v = v
                best_x = x_a
                best = a
        return translate_move(bot, best), best_v, best_x


def one_of(i, n):
    a = [0] * n
    a[i] = 1
    return np.array(a)


def q_action_nn(state, bot, s_key=None):
    x = get_state_x(state, bot, s_key=s_key)

    pos_of = {
        'W': 0,
        'A': 1,
        'S': 2,
        'D': 3,
        'Q': 4,
        'E': 5,
    }

    global qmap

    def q(a):
        #x_a = np.vstack([np.append(x, one_of(pos_of[str(a)], len(pos_of)))])
        #print_sk(s_key)
        q = qmap[str(a)].predict(x)[0][0]
        #print(str(a), q)
        return q, x

    valid_actions = [a for a in all_actions(bot) if translate_move(bot, a).validate(state, bot)]
    if random.random() < epsilon:
        a = random.choice(valid_actions)
        (v, x_a) = q(a)
        return translate_move(bot, a), v, x_a
    else:
        best = valid_actions[0]
        (best_v, best_x) = q(best)
        for a in valid_actions[1:]:
            (v, x_a) = q(a)
            if v > best_v:
                best_v = v
                best_x = x_a
                best = a
        return translate_move(bot, best), best_v, best_x



def translate_move(bot, action):
    """model chooses moves relative to bots face, this is translation to absolute move"""
    a = str(action)
    if a != "W" and a != "S" and a != "D" and a != "A":
        return action

    if bot.direction == Direction.RIGHT:
        return {"W": MoveRight(),
         "S": MoveLeft(),
         "D": MoveDown(),
         "A": MoveUp()}[a]
    elif bot.direction == Direction.UP:
        return {"W": MoveUp(),
                "S": MoveDown(),
                "D": MoveRight(),
                "A": MoveLeft()}[a]
    elif bot.direction == Direction.LEFT:
        return {"W": MoveLeft(),
                "S": MoveRight(),
                "D": MoveUp(),
                "A": MoveDown()}[a]
    elif bot.direction == Direction.DOWN:
        return {"W": MoveDown(),
                "S": MoveUp(),
                "D": MoveRight(),
                "A": MoveLeft()}[a]
    else: raise RuntimeError("Error in move translation")


def print_sk(s_key):
    for i in range(7):
        for j in range(7):
            print(s_key[i*7+j], end='')
        print()
    print()

def learning_run1(state, random_start=False):
    global qmap
    bot = state.bots[0]
    action_list = []
    total_reward = 0

    max_steps = state.height * state.width
    diagonal_len = math.sqrt(state.width ** 2 + state.height ** 2)

    # collect boosters
    # while True:
    #     #print(bot.pos)
    #     path = pathfinder.bfsFind(state, bot.pos, boosterP(state))
    #     if path is None: break
    #
    #     for (pos, nextPos) in zip(path, path[1:]):
    #         a = moveCommand(pos, nextPos)
    #         action_list.append(a)
    #         state.nextAction(a)

    # for i in range(state.boosters[Booster.MANIPULATOR]):
    #     a = AttachManipulator(ExperimentalAttacher(forward_wide).get_position(bot))
    #     if a.validate(state, bot):
    #         action_list.append(a)
    #         state.nextAction(a)

    # if random_start:
    #     start_pos = None
    #     while not start_pos or not state.cell(*start_pos)[1] == Cell.CLEAN:
    #         start_pos = (random.randint(0, state.width -1),
    #                      random.randint(0, state.height - 1))
    #     pass
    # else:
    #     start_pos = state.bots[0].pos
    # state.setBotPos(*start_pos)

    steps = 0
    steps_from_last_positive_r = 0
    rewarded_steps = 0

    def next_path(end_p):
        return pathfinder.bfsFindExt(state,
                                     bot.pos,
                                     end_p,
                                     wheels=bot.wheel_duration,
                                     drill=bot.drill_duration)
        # if bot.drill_duration > 3:
        #     return pathfinder.bfsFindExt(state, bot.pos,
        #                              lambda l, x, y: state.cell(x, y)[1] == Cell.ROT,
        #                              wheels=bot.wheel_duration,
        #                              drill=bot.drill_duration)
        # else:
        #     return pathfinder.bfsFind(state, bot.pos,
        #                               lambda l, x, y: state.cell(x, y)[1] == Cell.ROT)

    def go_to(end_p, path=None):
        if path is None: path = next_path(end_p)
        #print(path)
        if path:
            commands = []
            for (pos, nextPos) in zip(path, path[1:]):
                commands.append(moveCommand(pos, nextPos))
            # print(state.bots[0].pos, path)
            # print([str(c) for c in commands])
            for c in commands:
                if c.validate(state, state.bots[0]):
                    action_list.append(c)
                    state.nextAction(c)
                    nonlocal steps
                    steps += 1
            return True
        else: return False


    #goToRot = GoToClosestRot()
    #goToBooster = GoToBooster()

    sk = state_key(state)
    while not state.is_all_clean() and steps < max_steps:
        #print(steps, ": ")
        #print_sk(sk)

        # try to activate boosters
        # manipulators
        attached = False
        for i in range(state.boosters[Booster.MANIPULATOR]):
            attachers = [
                AttachManipulator(SimpleAttacher().get_position(bot)),
                AttachManipulator(ExperimentalAttacher(forward_wide).get_position(bot)),
                AttachManipulator(ExperimentalAttacher(forward).get_position(bot)),
                AttachManipulator(ExperimentalAttacher(experimental).get_position(bot)),
            ]
            random.shuffle(attachers)
            for a in attachers:
                if a.validate(state, bot):
                    action_list.append(a)
                    state.nextAction(a)
                    attached = True
                    break
        if attached:
            sk = state_key(state)
            continue
        # drill
        if state.boosters[Booster.DRILL] > 0:
            a = AttachDrill()
            if a.validate(state, bot):
                action_list.append(a)
                state.nextAction(a)
                sk = state_key(state)
                continue
        # wheel
        # print("checking wheels")
        if (state.boosters[Booster.WHEEL] > 0
                and (is_locally_visible(state, bot.pos, (0, 2))
                     or is_locally_visible(state, bot.pos, (2, 0))
                     or is_locally_visible(state, bot.pos, (-2, 0))
                     or is_locally_visible(state, bot.pos, (0, -2)))
        ):
            a = AttachWheels()
            if a.validate(state, bot):
                action_list.append(a)
                state.nextAction(a)
                sk = state_key(state)
                continue


        # see if priority booster lays nearby from time to time
        if rewarded_steps % (diagonal_len // 5) == 0:
            pb_endp = lambda l, x, y: state.cell(x, y)[0] in priority_boosters
            p = next_path(pb_endp)
            if p and len(p) < diagonal_len // 2:
                if go_to(pb_endp, path=p):
                    sk = state_key(state)
                    continue

        # if booster is very close
        if 'b' in sk:  # then go to booster
            # print('going to priority b')
            if go_to(lambda l, x, y: state.cell(x, y)[0] in boosters):
                sk = state_key(state)
                continue

        # if qbot does not see any rot cells
        if 'r' not in sk or steps_from_last_positive_r > 10:
            # then go to closest rot or priority_booster
            #print(steps_from_last_positive_r)
            #print('going to rot')
            if go_to(lambda l, x, y: (state.cell(x, y)[1] == Cell.ROT
                                      or state.cell(x, y)[0] in priority_boosters)):
                steps_from_last_positive_r = 0
                sk = state_key(state)
                #print(get_key(state, bot, GoToClosestRot()))
                #print_sk(sk)
                #print()
                continue
            elif bot.wheel_duration > 0:
                moved = False
                for m in all_actions(bot)[:4]:
                    if m.validate(state, bot):
                        moved = True
                        action_list.append(m)
                        state.nextAction(m)

                #print(bot.wheel_duration)
                #print_sk(sk)
                #encoder.Encoder.encode_action_lists("../q-sol/fail.sol", [action_list], len(action_list))
                if not moved: raise RuntimeError()
                sk = state_key(state)
                continue
            else:
                raise RuntimeError('go_to rot failed')
                return (None, state, total_reward)



        # Q-learning: off-policy temporal difference control
        #while 'r' in sk:
            # state is s
        (a, v, key) = q_action(state, bot, s_key=sk)
        #print(str(a), end='')

        action_list.append(a)
        state.nextAction(a)
        # state is s' now
        sk = state_key(state)
        steps += 1

        if state.last_painted > 0:
            r = state.last_painted
            steps_from_last_positive_r = 0
        else:
            steps_from_last_positive_r += 1
            #r = -1 - steps_from_last_positive_r * 0.05
        r = state.last_painted
        # update Q
        #print("r = " + str(r) + ", q = " + str(qmap[key]), end=" ")

        total_reward += r
        rewarded_steps += 1

        # update q(s, a)
        global epsilon
        # v1 = max_a(Q(s', a)), so set epsilon to 0 temporarily
        e, epsilon = epsilon, 0
        (_, v1, _) = q_action(state, bot, s_key=sk)
        qmap[key] = v + alpha * (r + gamma * v1 - v)
        epsilon = e

            # SARSA: on-policy temporal difference control
            # v1 = Q(s', a)
            # (v1, _) = q_value(state, bot, a, s_key=sk)
            # qmap[key] += alpha * (r + gamma * v1 - v)

        qmap["count of observations"] += 1

            #print("q1 = " + str(qmap[key]))

    if random_start: return False
    else: return action_list, state, total_reward / rewarded_steps


def in_vision_range(state, point, destination):
    # check if destination is locally visible from point
    (x1, y1) = point
    (x2, y2) = destination
    (dx, dy) = (x2 - x1, y2 - y1)
    if abs(dx) > 3 or abs(dy) > 3:
        return False
    else:
        return is_locally_visible(state, point, (dx, dy))


def rot_in_manipulator_range(state, bot, x, y, blob=None):
    #return state.cell(x, y)[1] == Cell.ROT and (blob is None or (x,y) in blob)

    for (dx, dy) in bot.manipulators + [(0, 0)]:
        dest = (x + dx, y + dy)
        # print(x, y, dest)
        # print("in map", state.in_map(dest))
        # if state.in_map(dest):
        #     print("is rot", state.cell(*dest)[1] == Cell.ROT)
        #     print("in blob", (blob is None or dest in blob))
        #     print("visible", in_vision_range(state, (x, y), dest))
        if (state.in_map(dest)
                and state.cell(*dest)[1] == Cell.ROT
                and (blob is None or dest in blob)
                and in_vision_range(state, (x, y), dest)):
            return True
    return False


def init_weights(state, bot):
    x = get_state_x(state, bot)
    w = np.random.rand(len(x) + len(all_actions(bot))) * 2e-5 - 1e-5
    print(w.shape)
    return w


def check_linear():
    real_w = np.array([1, 3, -2, 12], dtype=float)
    def y(x):
        return x.dot(real_w)

    alpha = 0.01
    w = np.random.rand(4)
    for i in range(10000):
        x = np.random.rand(4) * 5
        e = y(x) - x.dot(w)
        w += alpha * e * x
        print(e)
        print(w)

def tf_test():


    x = np.random.randint(0, 2, (1000, 20))

    print(tf.__version__)
    model = keras.Sequential([
        keras.layers.Dense(8, activation=tf.nn.relu, input_shape=[len(x[0])]),
        keras.layers.Dense(4, activation=tf.nn.relu),
        keras.layers.Dense(1, activation=tf.keras.activations.linear)
    ])

    def y(xs):
        return sum([x * 2 - 1 for x in xs])

    optimizer = keras.optimizers.RMSprop(0.1)

    # save_cb = tf.keras.callbacks.ModelCheckpoint(
    #     '../qmaps/model.tf', save_weights_only=True, period=100)

    model.compile(loss='mean_squared_error',
                  optimizer=optimizer,
                  metrics=['mean_absolute_error', 'mean_squared_error'],
                  )
    model.summary()
    model.load_weights('../qmaps/model.tf')

    labels = np.array([y(xs) for xs in x])
    print(labels.shape)

    print(x[0], x[0].shape)
    print(model.predict(x[:5]))


    #history = model.fit(x, labels, epochs=1000)
    print(x[:5], labels[:5])
    print(model.predict(x[:5]))

    #model.save_weights('../qmaps/model.tf')


prev_state_set = set()

def load_visited_set():
    global prev_state_set
    if os.path.isfile('../qmaps/visited_set.pickle'):
        with open('../qmaps/visited_set.pickle', 'rb') as f:
            return set(pickle.load(f))

def dump_visited_set():
    global prev_state_set
    with open('../qmaps/visited_set.pickle', 'wb+') as f:
        pickle.dump(list(prev_state_set), f)
        print('visited set dumped:', len(prev_state_set))

def learning_run1_in_region(qmap_par, state, blob, at_end_go_to=None, max_steps=None):
    bot = state.bots[0]

    global qmap
    qmap = qmap_par

    action_list = []
    total_reward = 0

    steps = 0
    steps_from_last_positive_r = 0
    rewarded_steps = 0
    agent_steps = 0

    to_clean = blob.copy()
    for p in blob:
        if state.cell(*p)[1] == Cell.CLEAN:
            to_clean.remove(p)


    train_data = {} # ak -> sk -> (state_action_x, Q)
    for ak in map(str, all_actions(bot)):
        train_data[ak] = {}

    global prev_state_set

    state_set = set()

    x = None

    def next_path(end_p):
        return pathfinder.bfsFindExt(state,
                                     bot.pos,
                                     end_p,
                                     wheels=bot.wheel_duration,
                                     drill=bot.drill_duration)

    def go_to(end_p, path=None, in_blob=True):
        nonlocal sk
        if in_blob:
            end_p_fun = lambda l, x, y: (x, y) in blob and end_p(l, x, y)
        else:
            end_p_fun = end_p
        if path is None:
            path = next_path(end_p_fun)
        #print(path)
        #print(len(to_clean))
        if path:
            commands = []
            for (pos, nextPos) in zip(path, path[1:]):
                commands.append(moveCommand(pos, nextPos))
            # print(state.bots[0].pos, path)
            # print([str(c) for c in commands])
            for c in commands:
                if c.validate(state, state.bots[0]):
                    action_list.append(c)
                    state.nextAction(c)
                    nonlocal steps
                    steps += 1
                    to_clean.difference_update(state.last_painted)


                    # let's also learn 'go_to' paths
                    sk = state_key(state)  # state is s' now
                    # x1 = get_state_x(state, bot, s_key=sk)
                    nonlocal agent_steps, r
                    agent_steps += 1

                    r = len(state.last_painted) - 1

                    nonlocal total_reward, rewarded_steps, full_state_key
                    total_reward += r
                    rewarded_steps += 1

                    full_state_key = get_key(state, bot, c, s_key=sk)

                    state_set.add(full_state_key)
                    train_data[str(c)][full_state_key[:-1]] = (x, r, total_reward, agent_steps)
                    #print('added data for', full_state_key )

            return True
        elif bot.wheel_duration > 0:
            moved = False
            for m in all_actions(bot)[:4]:
                if m.validate(state, bot):
                    moved = True
                    action_list.append(m)
                    state.nextAction(m)
            #print(bot.wheel_duration)
            # print_sk(sk)
            # encoder.Encoder.encode_action_lists("../q-sol/fail.sol", [action_list], len(action_list))
            if not moved: raise RuntimeError()
            sk = state_key(state)
            go_to(end_p, path=path, in_blob=in_blob)
        else: return False

    def _continue():
        nonlocal sk, a, x, to_clean
        sk = state_key(state)
        (a, _, x) = q_action_nn(state, bot, s_key=sk)
        to_clean.difference_update(state.last_painted)

    _continue()

    while len(to_clean) > 0 and steps < max_steps:
        #print_sk(sk)

        # try to activate boosters
        # manipulators

        if attach_manipulators(state, bot):
            _continue()
            continue
        else:
            #print_sk(sk)
            pass
        # # drill
        if state.boosters[Booster.DRILL] > 0:
            _a = AttachDrill()
            if _a.validate(state, bot):
                action_list.append(_a)
                state.nextAction(_a)
                _continue()
                continue
        # # wheel
        if (state.boosters[Booster.WHEEL] > 0
                and (is_locally_visible(state, bot.pos, (0, 2))
                     or is_locally_visible(state, bot.pos, (2, 0))
                     or is_locally_visible(state, bot.pos, (-2, 0))
                     or is_locally_visible(state, bot.pos, (0, -2)))
        ):
            _a = AttachWheels()
            if _a.validate(state, bot):
                action_list.append(_a)
                state.nextAction(_a)
                _continue()
                continue

        # if booster is very close
        if 'b' in sk:  # then go to booster
            #print('going to priority b')
            if go_to(lambda l, x, y: state.cell(x, y)[0] in boosters, in_blob=False):
                _continue()
                continue
            else:
                raise RuntimeError("can't go to booster")

        # if qbot does not see any rot cells or is being stupid
        if 'r' not in sk or steps_from_last_positive_r > 4:
            # then go to closest rot or
            if go_to(lambda l, x, y: rot_in_manipulator_range(state, bot, x, y, blob)):
                steps_from_last_positive_r = 0
                _continue()
                continue
            elif len(to_clean) == 0: break
            else:
                # TODO: FIX state.last_painted!!
                for p in blob:
                    if state.cell(*p)[1] == Cell.CLEAN and p in to_clean:
                        to_clean.remove(p)
                if len(to_clean) == 0: break
                print(to_clean)
                encoder.Encoder.encode_action_lists(
                    "../q-sol/fail.sol", state.actions(), 1)
                raise RuntimeError('go_to rot failed')

        # state is s
        full_state_key = get_key(state, bot, a, s_key=sk)

        action_list.append(a)
        state.nextAction(a)
        #print(str(a), end='')
        sk = state_key(state) # state is s' now
        #x1 = get_state_x(state, bot, s_key=sk)
        steps += 1
        agent_steps += 1
        to_clean.difference_update(state.last_painted)

        r = len(state.last_painted) - 1
        if len(state.last_painted) > 0:
            steps_from_last_positive_r = 0
        else:
            steps_from_last_positive_r += 1
            r -= steps_from_last_positive_r * 0.1

        total_reward += r
        rewarded_steps += 1

        (a1, v1, x1) = q_action_nn(state, bot, s_key=sk)

        state_set.add(full_state_key)
        train_data[str(a)][full_state_key[:-1]] = (x, r, total_reward, agent_steps)
        #print(full_state_key)

        x = x1
        a = a1

        # # update q(s, a)
        # global epsilon
        # # v1 = max_a(Q(s', a)), so set epsilon to 0 temporarily
        # e, epsilon = epsilon, 0
        # (_, v1, _) = q_action(state, bot, s_key=sk)
        # qmap[key] = v + alpha * (r + gamma * v1 - v)
        # epsilon = e

        # qmap["count of observations"] += 1

            #print("q1 = " + str(qmap[key]))

    print("Observed ", len(state_set), "unique state-action pairs", end=', ')
    if len(prev_state_set) > 0:
        _p = round(100.0 * (len(state_set) - len(state_set.intersection(prev_state_set))) / len(state_set))
        print(str(_p) + "% of them new", end='. ')
    print("R =", round(total_reward, 1))

    prev_state_set = prev_state_set.union(state_set)
    #dump_visited_set()

    # for sk in state_set.intersection(prev_state_set):
    #     a = sk[-1]
    #     x = train_data[str(a)][sk[:-1]][0]
    #     q = qmap[str(a)].predict(x)[0][0]
    #     print('before train:', sk[2:-1], str(a), q)
    #     (_, r, acc_r, i) = train_data[str(a)][sk[:-1]]
    #     q_real = r + (gamma ** (agent_steps - i - 1)) * (total_reward - acc_r)
    #     print('Q = ', q_real)
    #     print_sk(sk[2:-1])


    for ak in train_data:

        a_train_data = list(train_data[ak].values())

        if len(a_train_data) <= 0: continue
        #print(len(train_data), ' examples collected, ', end='')

        xs = np.vstack([xs for (xs, _, _, _) in a_train_data])
        qs = [r + (gamma ** (agent_steps - i - 1)) * (total_reward - acc_r) for (_, r, acc_r, i) in a_train_data]
        labels = np.vstack(qs)

        nn = qmap[ak]

        # res = nn.evaluate(xs, labels, verbose=0)
        # print("Untrained: ", res)

        #nn.fit(xs, labels, epochs=10, verbose=0)


        # for sk in state_set.intersection(prev_state_set):
        #     a = sk[-1]
        #     if a == ak:
        #         x = train_data[str(a)][sk[:-1]][0]
        #         q = qmap[str(a)].predict(x)[0][0]
        #         print('after train:', sk[2:-1], str(a), q)
        #         (_, r, acc_r, i) = train_data[str(a)][sk[:-1]]
        #         q_real = r + (gamma ** (agent_steps - i - 1)) * (total_reward - acc_r)
        #         print('Q = ', q_real)
        #         print_sk(sk[2:-1])

        for i in range(10):
            nn.train_on_batch(xs, labels)

    #     res = nn.evaluate(xs, labels, verbose=0)
    #     print("Trained: ", res)
    # print()


    if at_end_go_to:
        go_to(at_end_go_to, in_blob=False)

    #print(qmap["weights"])

    return state, max_steps is None or steps < max_steps



task_init_state = None
saved_task_id = None


def get_state(task_id):
    global task_init_state, saved_task_id
    if not task_init_state:
        filename = "../desc/" + task_id + ".desc"
        print(filename)
        task_init_state = State.decode(decode.parse_task(filename))
        saved_task_id = task_id
        return copy.deepcopy(task_init_state)
    elif saved_task_id == task_id:
        return copy.deepcopy(task_init_state)
    else:
        task_init_state = None
        return get_state(task_id)


def learn(task_id, qmap_fname):

    best_sol = None
    while not best_sol:
        (best_sol, s, r) = learning_run1(get_state(task_id), random_start=False)
    iterations = 100 #10000 // s.width

    best_len = len(best_sol)
    print(str(task_id) + " 0: " + str(best_len))
    results = [best_len]

    for i in range(1, iterations - 1):
        random_start = False
        (sol, _, r) = learning_run1(get_state(task_id), random_start=random_start)
        if sol is None:
            print("learning_run1 failed")
            continue
        results.append(len(sol))
        if iterations < 10 or i % (iterations // 10) == 0:
            print(str(task_id) + " " + str(i) + ": " + str(results[-1]) + " / " + str(best_len),
                  "Average reward:", round(r, 4))

        if not random_start and best_len >= len(sol):
            if best_len > len(sol):
                print(str(task_id) + " " + str(i) + ": " + str(best_len) + " / " + str(results[-1]),
                      "Average reward:", round(r, 4))
            best_sol = sol
            best_len = results[-1]

    print("Average result on this run:", round(sum(results) / len(results)))

    # with open(qmap_fname, "wb") as f:
    #     print("Dumping", qmap_fname, "with ", qmap["count of observations"], "observations")
    #     pickle.dump(qmap, f)


    #print(qmap)
    # with open(dumped_qmap_name, "rb") as f:
    #     qmap1 = pickle.load(f)
    #     for key in qmap:
    #         if qmap[key] != qmap1[key]:
    #             raise RuntimeError("BAD DUMP")
    return best_sol


def learn_regions(task_id, pathname):
    global qmap
    qmap = load_nn_qmap(get_state(task_id), pathname)
    load_visited_set()

    global prev_state_set
    prev_state_set = load_visited_set()
    print('visited set loaded:', len(prev_state_set))

    from solver import solve_with_regions
    best_sol = None
    regions_cache = None
    success = False

    global epsilon
    epsilon = 0.1

    fails = 0

    while not success:
        (s, regions_cache, success) = solve_with_regions(get_state(task_id), qmap, regions_cache)
        if success:
            best_sol = list(s.actions())[0]
        else:
            fails += 1

            if epsilon > 0.1:
                epsilon -= 0.01
            else:
                epsilon = 0.1
            print("start: failed with max_steps, set epsilon =", epsilon)
            #dump_nn_qmap(qmap, pathname)
            encoder.Encoder.encode_action_lists("../q-sol/" + task_id + "last.sol", s.actions())
            #if fails > 0: return

    iterations = 1000


    #alpha = 0.5


    best_len = len(best_sol)
    print(str(task_id) + " 0: " + str(best_len))
    results = [best_len]

    epsilon = 0.01

    for i in range(1, iterations - 1):
        #epsilon = 1.0 / (2 * i)
        #alpha = 1.0 / i

        (s, regions_cache, success) = solve_with_regions(get_state(task_id), qmap, regions_cache)
        dump_nn_qmap(qmap, pathname)
        #dump_visited_set()
        if not success:
            print(str(i) + ": failed with max_steps")
            #print(qmap)
            continue
        sol = list(s.actions())[0]

        if sol is None:
            print("No solution. Something went wrong")
            continue
        results.append(len(sol))
        if iterations < 10 or i % (iterations // 10) == 0:
            print(str(task_id) + " " + str(i) + ": " + str(results[-1]) + " / " + str(best_len))


        if best_len >= len(sol):
            if best_len > len(sol):
                print(str(task_id) + " " + str(i) + ": " + str(best_len) + " / " + str(results[-1]))
            best_sol = sol
            best_len = results[-1]

    print("Average result on this run:", round(sum(results) / len(results)))
    dump_nn_qmap(qmap, pathname)

    # with open(qmap_fname, "wb") as f:
    #     print("Dumping", qmap_fname, "with ", qmap["count of observations"], "observations")
    #     pickle.dump(qmap, f)


    #print(qmap)
    # with open(dumped_qmap_name, "rb") as f:
    #     qmap1 = pickle.load(f)
    #     for key in qmap:
    #         if qmap[key] != qmap1[key]:
    #             raise RuntimeError("BAD DUMP")
    return best_sol


def q_action_no_e(state, prev_actions):
    l = [str(a) for a in prev_actions[len(prev_actions)-20:]]
    if l and len(set(l)) == 2:
        return GoToClosestRot(), None
    else:
        return q_action(state)

def run_qbot(state, qmap_fname):
    global qmap

    qmap_fname = qmap_fname

    if os.path.isfile(qmap_fname):
        with open(qmap_fname, 'rb') as f:
            qmap = pickle.load(f)
    else:
        raise RuntimeError('Not found: ' + qmap_fname)

    global epsilon
    epsilon = 0  # no exploration
    res = None
    while not res:
        (res, final_state) = learning_run1(state)

    print(final_state.tickNum)
    return final_state


def merge_qmaps(qmap_list):
    acc_qmap = {}
    for qmap in qmap_list:
        for key in qmap:
            if key in acc_qmap:
                acc_qmap[key].append(qmap[key])
            else:
                acc_qmap[key] = [qmap[key]]
    res_qmap = {}
    for key in acc_qmap:
        res_qmap[key] = sum(acc_qmap[key]) / len(acc_qmap[key])

    return res_qmap


def merge_main(args):
    res_qmap_fname = args[0]

    qmaps = []
    for qmap_fname in args[1:]:
        with open(qmap_fname, 'rb') as f:
            qmap = pickle.load(f)
            qmaps.append(qmap)

    res_qmap = merge_qmaps(qmaps)
    with open(res_qmap_fname, "wb+") as f:
        pickle.dump(res_qmap, f)

def initialize_nn_qmap(state):
    n = len(state_key_to_bitarray(state_key(state))) + 2
    map = {}
    for action in all_actions(state.bots[0]):

        model = keras.Sequential([
            keras.layers.Dense(50, activation=tf.nn.relu, input_shape=[n]),
            keras.layers.Dense(6, activation=tf.nn.relu),
            keras.layers.Dense(1, activation=tf.keras.activations.linear),
        ])

        optimizer = keras.optimizers.RMSprop(1e-2)

        model.compile(loss='mean_squared_error',
                      optimizer=optimizer,
                      metrics=['mean_absolute_error', 'mean_squared_error'],
                    )
        model.summary()
        map[str(action)] = model

    return map


def dump_nn_qmap(map, pathname):
    for key in map:
        map[key].save_weights(pathname + "_" + key)


def load_nn_qmap(state, pathname):
    map = initialize_nn_qmap(state)
    for key in map:
        path = pathname + "_" + key
        if os.path.isfile(path):
            map[key].load_weights(pathname + "_" + key)
    return map


def _main(args):
    if args and len(args) >= 3:
        print(args)
        if args[0] == 'merge':
            if args: merge_main(args[1:])
            else: print('usage: merge result_qmap qmap1 qmap2 ...')
            return

        k1 = int(args[0])
        k2 = int(args[1])
        qmap_fname = args[2]

        for i in range(k1, k2):
            task_id = "prob-"
            if i < 10: task_id += "00" + str(i)
            elif i < 100: task_id += "0" + str(i)
            else: task_id += str(i)

            al = learn_regions(task_id, qmap_fname)

            print("res for " + str(task_id) + ": " + str(len(al)))
            encoder.Encoder.encode_action_lists("../q-sol/" + task_id + ".sol", [al], len(al))

        #qmap.save_weights(qmap_fname)


    else: print('Not enough arguments')



if __name__ == '__main__':
    args = sys.argv[1:]
    _main(args)



