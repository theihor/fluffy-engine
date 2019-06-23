import copy
import pathfinder
from constants import *
from actions import *


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


def runActions(st, actions):
    for action in actions:
        st.nextAction(action)


def findPath(st, from_pos, to_pos):
    return pathfinder.bfsFind(st, from_pos, lambda l, x, y: (x, y) == to_pos)


def last_manipulator_attached(log):
    for i in reversed(range(len(log))):
        if isinstance(log[i].action, AttachManipulator):
            return i
    return -1


def get_teleports(log):
    last_teleport = 0
    num_teleports = 0
    for i in range(len(log)):
        if log[i].picked_booster == Booster.TELEPORT:
            last_teleport = i
            num_teleports += 1
    return (num_teleports, last_teleport)


def log_sections(st, bot_num):
    bot = st.bots[bot_num]
    log = bot.log
    sections = []
    start_ind = 0
    section_start = start_ind
    section_clean = False
    for i in range(start_ind, len(log)):
        if (log[i].num_cleaned == 0) != section_clean:
            if i != section_start:
                sections.append((section_start, i - 1, section_clean))
                section_start = i
                section_clean = log[i].num_cleaned == 0
            else:
                section_clean = log[i].num_cleaned == 0
    sections.append((section_start, len(log) - 1, section_clean))
    return sections


OPT_CLEAN_RANGE = 3


def previous_visit(st, init_st, pos, num_bot, num_action):

    def get_first_visit(pos):
        (x, y) = pos
        bot_log_set = st.cells_log[y][x]
        if bot_log_set is None:
            return None
        bot_log = bot_log_set.get(num_bot)
        if bot_log is not None:
            first_visit = bot_log[0]
            return first_visit
        return None

    def end(l, x, y):
        first_visit = get_first_visit((x, y))
        if first_visit is not None:
            return first_visit < num_action
        return False
    if end(0, pos[0], pos[1]):
        return get_first_visit(pos)
    path_to_prev = pathfinder.bfsFindClosest(init_st, pos, end,
                                             max_path_len=OPT_CLEAN_RANGE,
                                             rank=lambda x, y: get_first_visit((x, y)))
    if path_to_prev is None:
        return None
    res_pos = path_to_prev[len(path_to_prev) - 1]
    return get_first_visit(res_pos)


def optimize_small_clean(init_st, st, bot, bot_num, sections):
    changes = []
    if sections[0][2]:
        sect_iter = zip(sections[::2], sections[1::2])
    else:
        sect_iter = zip(sections[1::2], sections[2::2])
    log = bot.log
    start_ind = last_manipulator_attached(log) + 1
    for ((start1, end1, clean), (start2, end2, not_clean)) in sect_iter:
        pos = log[start2].pos
        prev_visit = previous_visit(st, init_st, pos, bot_num, start2)
        if prev_visit is None:
            continue
        if start1 < start_ind or prev_visit < start_ind:
            continue
        # if ((end2 - start2 + 4 * OPT_CLEAN_RANGE) < end1 - start1 and prev_visit is not None and prev_visit + 10 < start1):
        if (end1 - start1 > 30 and prev_visit is not None and prev_visit + 10 < start1):
            # print('Found opt possibility', (start1, end1, clean), (start2, end2, not_clean), 'to', prev_visit)
            change_list1 = [('go', log[prev_visit].pos, log[start2 - 1].pos),
                            ('prev', start2, end2),
                            ('go', log[end2].pos, log[prev_visit].pos)]
            changes.append((prev_visit, change_list1))
            # change_list2 = [('remove', end2)]
            # if end2 < len(log) - 1:
            #     change_list2.append(('go', log[start1-1].pos, log[end2].pos))
            # changes.append((start1 - 1, change_list2))
    return changes


def optimize_long_moves(init_st, st, bot, bot_num, sections):
    changes = []
    log = bot.log

    def no_boosters(start, end):
        if log[start].wheel_duration > 0 or log[start].drill_duration > 0:
            return False
        for i in range(start, end+1):
            if log[i].picked_booster is not None or log[i].action.booster_action():
                return False
        return True

    for ((start, end, clean), i) in zip(sections, range(len(sections))):
        if clean and no_boosters(start, end):
            change_list1 = [('remove', end)]
            if i != len(sections) - 1 and log[start-1].pos != log[end].pos:
                change_list1.append(('go', log[start-1].pos, log[end].pos))
            changes.append((start-1, change_list1))
    return changes


def optimize_teleports(init_st, st, bot, bot_num, sections):
    changes = []
    log = bot.log

    (num_teleports, last_teleport) = get_teleports(log)
    if num_teleports == 0:
        return []

    def no_boosters(start, end):
        if log[start].wheel_duration > 0 or log[start].drill_duration > 0:
            return False
        for i in range(start, end+1):
            if log[i].picked_booster is not None or log[i].action.booster_action():
                return False
        return True

    sorted_sections = list(sorted(filter(lambda x: x[2] and x[1] > last_teleport and no_boosters(x[0], x[1]), sections),
                                  key=lambda x: x[0] - x[1]))
    num_converted = 0
    prev_removed = []
    for ((start, end, clean), i) in zip(sorted_sections, range(len(sorted_sections))):
        prev_visit = previous_visit(st, init_st, log[end].pos, bot_num, max(start, last_teleport))
        if prev_visit is None:
            continue
        if prev_visit > start or prev_visit < last_teleport:
            continue
        for (s, e) in prev_removed:
            if e <= prev_visit <= e:
                prev_visit = None
        if prev_visit is None:
            continue
        change_list1 = [('remove', end), ('teleport', log[prev_visit].pos), ('go', log[prev_visit].pos, log[end].pos)]
        changes.append((start-1, change_list1))
        changes.append((prev_visit, [('set_pod',)]))
        num_converted += 1
        prev_removed.append((start, end))
        if num_converted == num_teleports:
            break
    return changes


def optimize(init_st, actions, bot_num, optimizer):
    st = copy.deepcopy(init_st)
    st.set_save_log()
    runActions(st, actions)

    bot = st.bots[bot_num]
    sections = log_sections(st, bot_num)

    # print('sections', sections)
    # print('orig actions', list(map(str, bot.actions)))
    changes = optimizer(init_st, st, bot, bot_num, sections)
    changes = list(sorted(changes, key=lambda x: x[0]))
    new_actions = []
    last_index = 0
    for (ind, updates) in changes:
        if ind >= last_index:
            # print('add', list(map(str, bot.actions[last_index:ind+1])))
            new_actions += bot.actions[last_index:ind+1]
            last_index = ind + 1
        for update in updates:
            # print('update', ind, update)
            if update[0] == 'go':
                (a, start, target) = update
                if start != target:
                    acts = pathToCommands(findPath(init_st, start, target))
                    # print('add new', list(map(str, acts)))
                    new_actions += acts
            elif update[0] == 'prev':
                (a, start, end) = update
                new_actions += bot.actions[start:end+1]
            elif update[0] == 'remove':
                (a, end) = update
                # print('remove', list(map(str, bot.actions[last_index:end+1])))
                last_index = end + 1
            elif update[0] == 'set_pod':
                new_actions.append(Reset())
            elif update[0] == 'teleport':
                (a, pos) = update
                new_actions.append(Shift(pos))
    if last_index <= len(bot.actions) - 1:
        new_actions += bot.actions[last_index:]
    st1 = copy.deepcopy(init_st)
    print('optimized to', len(new_actions))
    # print('optimized actions', list(map(str, new_actions)))
    runActions(st1, new_actions)
    return st1
