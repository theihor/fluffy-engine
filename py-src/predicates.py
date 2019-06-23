from constants import *


# called on collecting boosters stage
def boosterP(st):
    return lambda l, x, y: st.cell(x, y)[0] in COLLECTABLE


def usableP(st):
    return lambda l, x, y: st.cell(x, y)[0] is not None


# called for pathfinding when paining cells
def wrapP(st):
    return lambda l, x, y: st.cell(x, y)[1] == Cell.ROT \
                           or st.cell(x, y)[0] in USABLE


def spawnP(st):
    return lambda l, x, y: st.cell(x, y)[0] == Booster.MYSTERIOUS


# is the cell available for bot_num
def drillableP(st, bot=None):
    if bot is None:
        bot = st.bots[0]
    drill = bot.drill_duration
    wheel = bot.wheel_duration

    def drill_aval(l):
        # TODO (wheel handling)
        return drill > l

    return lambda l, x, y: drill_aval(l) or st.cell(x, y)[1] is not Cell.OBSTACLE


def parallelP(st, aimed):
    return lambda l, x, y: (x, y) not in aimed and \
                           (st.cell(x, y)[1] == Cell.ROT
                            or st.cell(x, y)[0] in USABLE)


# is the cell available if DRILL is used before pathfinding
def withDrillP(st):
    return lambda l, x, y: DRILL_DURATION > l or st.cell(x, y)[1] is not Cell.OBSTACLE
