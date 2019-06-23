import random

import pathfinder
from actions import *
from predicates import *
from solver import selectCommand, moveCommand

actions = [[]]


def pathToCommands(path, state, bot_num):
    commands = []
    for (pos, nextPos) in zip(path, path[1:]):
        command = moveCommand(pos, nextPos)
        if TURN_BOT:
            new = selectCommand(state, command, bot_num)
            if new != command:
                commands.append(new)
        commands.append(command)
    global actions
    actions[bot_num] += commands


def useClone(st, bot_num):
    bot = st.bots[bot_num]
    path = pathfinder.bfsFind(st, bot.pos,
                              spawnP(st),
                              availP=drillableP(st, bot))
    if path is None:
        print('Cant use SPAWN')
        return
    print('Go to SPAWN')
    pathToCommands(path, st, bot_num)
    global actions
    actions[bot_num].append(CloneAction())


boostersAvailable = True


def collectBoosters(st, bot_num):
    global boostersAvailable
    if not boostersAvailable:
        return False
    bot = st.bots[bot_num]
    path = pathfinder.bfsFind(st, bot.pos,
                              boosterP(st),
                              availP=drillableP(st, bot))
    if path is None:
        boostersAvailable = False
        return False
    pathToCommands(path, st, bot_num)
    return True


def useBooster(st, bot_num):
    bot = st.bots[bot_num]
    ret_val = False
    if st.boosters[Booster.MANIPULATOR] > 0:
        command = AttachManipulator(ATTACHER.get_position(bot))
        global actions
        actions[bot_num].append(command)
        ret_val = True
    if st.boosters[Booster.CLONE] > 0:
        useClone(st, bot_num)
        ret_val = True
    return ret_val


def parallelRotSolver(st, bot_num):
    global actions
    bot = st.bots[bot_num]
    path = pathfinder.bfsFind(st, bot.pos,
                              wrapP(st),
                              availP=drillableP(st))
    # if st.boosters[Booster.DRILL] > 0 and bot.drill_duration <= 0:
    #     path2 = pathfinder.bfsFind(st, bot.pos,
    #                                wrapP(st),
    #                                availP=withDrillP(st))
    #     if path2 is not None and len(path2) < len(path):
    #         # print("Attach DRILL at " + str(len(bot.actions)))
    #         actions[bot_num].append(AttachDrill())
    #         path = path2
    if path is None:
        return False
    pathToCommands(path, st, bot_num)
    if st.boosters[Booster.WHEEL] > 0 and bot.wheel_duration <= 0:
        if random.random() > WHEELS_PROC:
            # print("Attach WHEELS at " + str(len(bot.actions)))
            actions[bot_num].append(AttachWheels())
    if st.boosters[Booster.DRILL] > 0 and bot.drill_duration <= 0:
        if random.random() > DRILL_PROC:
            # print("Attach DRILL at " + str(len(bot.actions)))
            actions[bot_num].append(AttachDrill())
    return True


def drunkMasters(st):
    global actions
    collectBoosters(st, 0)
    step = 0
    while True:
        if all([len(x) > 0 for x in actions]):
            st.nextActions([x[0] for x in actions])
            # print(step)
            if step == 13032:
                break
            step += 1
            i = 0
            for x in actions:
                if len(x) > 0 and isinstance(x[0], CloneAction):
                    if len(st.bots) > len(actions):
                        print('Create new actions')
                        actions += [[]]
                    print("Clone action")
                i += 1
            for i in range(0, len(actions)):
                actions[i] = actions[i][1:]
        bot_num = 0
        for x in actions:
            if len(x) == 0:
                if bot_num == 0:
                    useBooster(st, bot_num)
                else:
                    a =1
                    pass
                if bot_num > 0 or not collectBoosters(st, bot_num):
                    parallelRotSolver(st, bot_num)
            bot_num += 1
        if all([len(x) == 0 for x in actions]):
            break
    return st
