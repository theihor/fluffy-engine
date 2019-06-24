from constants import STRICT_VALIDATION, Booster, Direction


class LoggedAction:
    def __init__(self, bot, action, direction):
        self.pos = bot.pos
        self.manip_num = len(bot.manipulators)
        self.wheel_duration = bot.wheel_duration
        self.drill_duration = bot.drill_duration
        self.action = action
        self.direction = direction
        self.num_cleaned = bot.last_clean_num
        self.picked_booster = bot.last_booster


class Bot:
    def __init__(self, pos: tuple, save_log=False):
        self.pos = pos
        self.manipulators = [
            (1, 0),
            (1, 1),
            (1, -1),
        ]
        self.wheel_duration = 0
        self.drill_duration = 0
        self.actions = []
        self.save_log = save_log
        if self.save_log:
            self.log = []
            self.last_clean_num = 0
            self.last_booster = None

    def is_attachable(self, x: int, y: int):
        coords = self.manipulators + [(0, 0)]

        if any(pos[0] == x and pos[1] == y for pos in coords):
            return False

        def true(pos: tuple):
            return abs(pos[0] - x) + abs(pos[1] - y) == 1

        return any(true(pos) for pos in coords)

    def attach(self, x: int, y: int):
        if STRICT_VALIDATION and not self.is_attachable(x, y):
            raise RuntimeError("Can't attach manipulator")
        self.manipulators.append((x, y))

    def turnLeft(self):
        def new(pos):
            return -pos[1], pos[0]
        self.manipulators = [new(pos) for pos in self.manipulators]

    def turnRight(self):
        def new(pos):
            return pos[1], -pos[0]
        self.manipulators = [new(pos) for pos in self.manipulators]

    def process(self, state):
        bot_cell = state.cell(self.pos[0], self.pos[1])
        if bot_cell[0] is not None:
            state.removeBooster(self.pos)
            print('Collected ', state.tickNum, str(bot_cell[0]))
            state.boosters[bot_cell[0]] += 1
            # state.lockBoosters = 2
        if self.save_log:
            if self.last_booster is None:
                self.last_booster = bot_cell[0]
        self.repaint(state)

    def repaint(self, state):
        def real(pos):
            return pos[0] + self.pos[0], pos[1] + self.pos[1]
        coords = [real(pos) for pos in self.manipulators] + [self.pos]
        num_painted = 0
        for pos in coords:
            num_painted += state.paintCell(*pos, *self.pos)
        if self.save_log:
            self.last_clean_num += num_painted

    def repaintWith(self, fromPos, state, func):
        def real(pos):
            return pos[0] + fromPos[0], pos[1] + fromPos[1]
        coords = [real(pos) for pos in self.manipulators] + [fromPos]
        for (x, y) in coords:
            state.tryPaintCellWith(fromPos[0], fromPos[1], x, y, func)

    def tickTime(self):
        if self.wheel_duration > 0:
            self.wheel_duration -= 1
        if self.drill_duration > 0:
            self.drill_duration -= 1

    def log_action(self, action):
        logged = LoggedAction(self, action, Direction.RIGHT)
        self.log.append(logged)

    def addDoNothing(self):
        from actions import DoNothing
        self.actions.append(DoNothing())
