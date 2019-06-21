from enum import Enum, auto

from parsec import *

nat = many1(digit()).parsecmap(lambda lst: int(''.join(lst)))

point = string("(").compose(
    separated(nat, string(","), 2, 2, end=False).parsecmap(tuple)).skip(string(")"))

a_map = sepBy(point, string(","))


class Booster(Enum):
    B = auto()
    F = auto()
    L = auto()
    X = auto()


booster_code_dict = {
    "B": Booster.B,
    "F": Booster.F,
    "L": Booster.L,
    "X": Booster.X
}

booster_code = one_of("BFLX").parsecmap(lambda c: booster_code_dict[c])
booster_location = booster_code.bind(lambda x: point.parsecmap(lambda p: (x, p)))

obstacles = sepBy(a_map, string(";"))
boosters = sepBy(booster_location, string(";"))

sharp = string("#")


def task_from_list(lst):
    if len(lst[2]) == 1 and not lst[2][0]:
        os = []
    else:
        os = lst[2]
    return {"map": lst[0],
            "start": lst[1],
            "obstacles": os,
            "boosters": lst[3]}


task = a_map.bind(lambda parsed_map: sharp.compose(point.parsecmap(lambda p: [parsed_map, p])))\
   .bind(lambda lst1: sharp.compose(obstacles.parsecmap(lambda os: lst1 + [os])))\
   .bind(lambda lst2: sharp.compose(boosters.parsecmap(lambda bs: lst2 + [bs])))\
   .parsecmap(task_from_list)


def parse_task(filename):
    with open(filename, "r") as f:
        return task.parse(''.join(f.readlines()))
