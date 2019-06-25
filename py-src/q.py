import pathfinder
from constants import *
from predicates import drillableP, boosterP
from solver import moveCommand, collectBoosters
from actions import *
import random
import decode
import encoder
import copy
import os
import pickle
import sys


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

qmap = {}


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


epsilon = 0.001
alpha = 0.02 # learning rate
gamma = 0.98  # discount factor

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
    if state.cell(bx + dx, by + dy)[1] == Cell.OBSTACLE:
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
            if (x, y) in ms:
                arr.append('m')
                return
            (booster, c) = state.cell(x, y)
            if booster in priority_boosters:
                if is_visible(x, y): arr.append('b')
                else: arr.append('i')
                return

            if c == Cell.ROT:

                # if is_visible(x, y) != state.visible((x, y)):
                #     #print((bx - x, by - y))
                #     raise RuntimeError("is_visible failed!")

                if is_visible(x, y):
                    arr.append('r')
                else:
                    arr.append('i')
                #arr.append('r')
            elif c == Cell.OBSTACLE:
                arr.append('o')
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


def q_value(state, bot, action, s_key=None):
    key = get_key(state, bot, action, s_key=s_key)
    if key not in qmap:
        #return -1e-5 + random.random() * 2e-5, key
        return 0.2, key
    else:
        return qmap[key], key


def q_action(state, bot, s_key=None):
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

def learning_run1(state, random_start=False):

    bot = state.bots[0]
    action_list = []
    total_reward = 0

    max_steps = state.height * state.width

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

    def next_path(end_p):
        return pathfinder.bfsFindExt(state, bot.pos,
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

    def go_to(end_p):
        path = next_path(end_p)
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

        if 'b' in sk:  # then go to booster
            # print('going to priority b')
            if go_to(lambda l, x, y: state.cell(x, y)[0] in priority_boosters):
                sk = state_key(state)
                continue
            else:
                return (None, state, total_reward)

        if 'r' not in sk or steps_from_last_positive_r > 10: # then go to closest rot
            # drill
            if state.boosters[Booster.DRILL] > 0:
                a = AttachDrill()
                if a.validate(state, bot):
                    action_list.append(a)
                    state.nextAction(a)
                    sk = state_key(state)
                    continue
            # wheel
            if (state.boosters[Booster.WHEEL] > 0
                    # and (is_locally_visible(state, bot.pos, (0, 2))
                    #      or is_locally_visible(state, bot.pos, (2, 0))
                    #      or is_locally_visible(state, bot.pos, (-2, 0))
                    #      or is_locally_visible(state, bot.pos, (0, -2)))
            ):
                a = AttachWheels()
                if a.validate(state, bot):
                    action_list.append(a)
                    state.nextAction(a)
                    sk = state_key(state)
                    continue

            #print(steps_from_last_positive_r)
            #print('going to rot')
            if go_to(lambda l, x, y: (state.cell(x, y)[1] == Cell.ROT
                                      or state.cell(x, y)[0] in boosters)):
                steps_from_last_positive_r = 0
                sk = state_key(state)
                #print(get_key(state, bot, GoToClosestRot()))
                continue
            elif bot.wheel_duration > 0:
                #print(bot.wheel_duration)
                #print_sk(sk)
                #raise RuntimeError()
                action_list.append(DoNothing())
                state.nextAction(DoNothing())
                continue
            else:
                raise RuntimeError('go_to rot failed')
                return (None, state, total_reward)

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



        # state is s
        (a, v, key) = q_action(state, bot, s_key=sk)
        #print(str(a), end='')
        r = 0
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
            r = -1 - steps_from_last_positive_r * 0.05

        # update Q
        #print("r = " + str(r) + ", q = " + str(qmap[key]), end=" ")

        total_reward += r

        # Q-learning: off-policy temporal difference control
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
    else: return action_list, state, total_reward


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
    iterations = 10 #40000 // s.width

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
        #if iterations < 10 or i % (iterations // 5) == 0:
        print(str(task_id) + " " + str(i) + ": " + str(results[-1]) + " / " + str(best_len),
                  "Total reward:", round(r, 2))

        if not random_start and best_len >= len(sol):
            if best_len > len(sol):
               print(str(task_id) + " " + str(i) + ": " + str(results[-1]))
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

        global qmap

        if os.path.isfile(qmap_fname):
            with open(qmap_fname, 'rb') as f:
                print("Loading qmap...")
                qmap = pickle.load(f)
            print("Loaded qmap with",
                  qmap["count of observations"],
                  "observations and",
                  len(qmap),
                  "states observed at least once")
        if "count of observations" not in qmap:
            qmap["count of observations"] = 0

        for i in range(k1, k2):
            task_id = "prob-"
            if i < 10: task_id += "00" + str(i)
            elif i < 100: task_id += "0" + str(i)
            else: task_id += str(i)
            al = learn(task_id, qmap_fname)
            print("res for " + str(task_id) + ": " + str(len(al)))
            encoder.Encoder.encode_action_lists("../q-sol/" + task_id + ".sol", [al], len(al))

        with open(qmap_fname, "wb") as f:
            print("Dumping", qmap_fname, "with ",
                  str(round(qmap["count of observations"] * 1e-6, 1)) + "M",
                  "observations")
            pickle.dump(qmap, f)
    else: print('Not enough arguments')



if __name__ == '__main__':
    args = sys.argv[1:]
    _main(args)



