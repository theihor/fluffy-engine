import random

import pathfinder
import solver
from actions import *
from predicates import *
from solver import selectCommand, moveCommand

actions = [[]]
aimed = [(-1, -1)]


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
    aimed[bot_num] = path[-1]
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


def collectBoosters(st, bot_num, pred=boosterP):
    global boostersAvailable
    if not boostersAvailable:
        return False
    bot = st.bots[bot_num]
    path = pathfinder.bfsFind(st, bot.pos,
                              pred(st),
                              availP=drillableP(st, bot))
    if path is None:
        boostersAvailable = False
        return False
    pathToCommands(path, st, bot_num)
    return True


def useBooster(st, bot_num):
    bot = st.bots[bot_num]
    if st.boosters[Booster.MANIPULATOR] > 0:
        command = AttachManipulator(ATTACHER.get_position(bot))
        global actions
        actions[bot_num].append(command)
        return True
    if st.boosters[Booster.CLONE] > 0:
        useClone(st, bot_num)
        return True
    return False


def parallelRotSolver(st, bot_num):
    global actions
    bot = st.bots[bot_num]
    path = pathfinder.bfsFind(st, bot.pos,
                              parallelP(st, aimed),
                              availP=drillableP(st, bot))
    # if AttachDrill().validate(st, bot):
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
    global actions, aimed
    collectBoosters(st, 0)
    step = 0
    while not st.is_cleaned():
        if all([len(x) > 0 for x in actions]):
            st.nextActions([x[0] for x in actions])
            print("{}: {}".format(step, st.clean_left))
            # if step == 829:
            #     break
            step += 1
            if len(st.bots) > len(actions):
                print('Create new actions')
                actions += [[]]
                aimed += [(-1, -1)]
                collectBoosters(st, len(st.bots) - 1, usableP)
            for i in range(0, len(actions)):
                if len(actions[i]) <= 0:
                    continue
                last_com: SimpleAction = actions[i][-1]
                if not last_com.booster_action() and st.cells[aimed[i][1]][aimed[i][0]][1] == Cell.CLEAN:
                    actions[i] = []
                elif isinstance(last_com, CloneAction) and not last_com.validate(st, st.bots[i]):
                    actions[i] = []
                else:
                    actions[i] = actions[i][1:]
        bot_num = 0
        for x in actions:
            if len(x) == 0:
                useBooster(st, bot_num)
                if bot_num > 0 or not collectBoosters(st, bot_num):
                    if not parallelRotSolver(st, bot_num):
                        actions[bot_num].append(DoNothing())
            bot_num += 1
        if all([len(x) == 0 for x in actions]):
            break

    while st.clean_left_f() != 0:
        print("{}: {}".format(step, st.clean_left))
        if all([len(x) > 0 for x in actions]):
            st.nextActions([x[0] for x in actions])
            step += 1
            for i in range(0, len(actions)):
                actions[i] = actions[i][1:]
        # TODO (fix for parallel)
        # bot_num = 0
        # for x in actions:
        #     if len(x) == 0:
        #         if not parallelRotSolver(st, bot_num):
        #             st.show()
        #             assert False
        #     bot_num += 1
        solver.closestRotSolver(st, 0)
    assert st.clean_left_f() == 0
    return st
