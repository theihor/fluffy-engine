import os
import pickle
import random

import decode
from constants import *
from encoder import Encoder
from actions import *
import pathfinder
import svgwrite
import svg_colors
from predicates import *
import copy
from optimizer import optimize, optimize_small_clean, optimize_long_moves, optimize_teleports
import networkx as nx
import postman_problems.solver
import csv
import tempfile
import sklearn.cluster
import numpy as np
import math
import disjoint_set
import pprint
import q


def solve(taskFile, solutionFile, solver, add_score=True):
    st = State.decode(decode.parse_task(taskFile))
    init_st = copy.deepcopy(st)
    new_state = solver(st)
    # for it in range(1):
    #     new_state = optimize(init_st, new_state.bots[0].actions, 0, optimize_small_clean)
    #     new_state = optimize(init_st, new_state.bots[0].actions, 0, optimize_long_moves)
    #     new_state = optimize(init_st, new_state.bots[0].actions, 0, optimize_teleports)
    Encoder.encodeToFile(solutionFile, new_state, add_score=add_score)




def selectCommand(state, command, bot_num):
    results = []
    bot = state.bots[bot_num]
    (x, y) = bot.pos
    current = len(bot.manipulators)
    if isinstance(command, MoveUp):
        current = numCleaned(state, (x, y + 1), bot_num)
    elif isinstance(command, MoveDown):
        current = numCleaned(state, (x, y - 1), bot_num)
    elif isinstance(command, MoveRight):
        current = numCleaned(state, (x + 1, y), bot_num)
    elif isinstance(command, MoveLeft):
        current = numCleaned(state, (x - 1, y), bot_num)
    results.append((current, command))
    bot.turnRight()
    right = numCleaned(state, bot.pos, bot_num)
    if TurnRight().validate(state, bot):
        results.append((right, TurnRight()))
    bot.turnLeft()
    bot.turnLeft()
    left = numCleaned(state, bot.pos, bot_num)
    if TurnLeft().validate(state, bot):
        results.append((left, TurnLeft()))
    bot.turnRight()
    command = max(results, key=lambda t: t[0])[1]
    return command


# def pathToCommands(path, state, bot_num=0):
#     commands = []
#     for (pos, nextPos) in zip(path, path[1:]):
#         commands.append(moveCommand(pos, nextPos))
#     for command in commands:
#         if TURN_BOT:
#             new = selectCommand(state, command, bot_num)
#             if new != command:
#                 state.nextAction(new)
#         state.nextAction(command)


def pathToCommands(path, state, bot_num=0):
    original_path_sells_state = {}
    last_pos = path[-1]
    for (pos, nextPos) in zip(path, path[1:]):
        original_path_sells_state.update({nextPos: state.cells[nextPos[1]][nextPos[0]][1]})
    for (pos, nextPos) in zip(path, path[1:]):
        # if during bot movement target pos is already wrapped by his manipulators
        # then we need to stop moving towards that point and select another

        # check for last position
        if original_path_sells_state[last_pos] != state.cells[last_pos[1]][last_pos[0]][1]:
            break;
        # check for next position
        if original_path_sells_state[nextPos] != state.cells[nextPos[1]][nextPos[0]][1]:
            break

        command = moveCommand(pos, nextPos)
        if TURN_BOT:
            new = selectCommand(state, command, bot_num)
            if new != command:
                state.nextAction(new)
        state.nextAction(command)


def collectBoosters(st, bot_num):
    bot = st.bots[bot_num]
    while True:
        path = pathfinder.bfsFind(st, bot.pos,
                                  boosterP(st),
                                  availP=drillableP(st, bot))
        if path is None:
            break
        pathToCommands(path, st, bot_num)

        if st.boosters[Booster.MANIPULATOR] > 0:
            command = AttachManipulator(ATTACHER.get_position(bot))
        # TODO (all boosters)
        else:
            continue
        st.nextAction(command)


def collect_boosters2(state, bot_num):
    bot = state.bots[bot_num]
    while True:
        #print(bot.pos)
        path = pathfinder.bfsFind(state, bot.pos, boosterP(state))
        if path is None: break

        for (pos, nextPos) in zip(path, path[1:]):
            m = moveCommand(pos, nextPos)
            state.nextAction(m)
        a = AttachManipulator(ExperimentalAttacher(forward_wide).get_position(bot))
        if a.validate(state, bot):
            state.nextAction(a)
        else:
            print('Cant attach manipulator :(')



def closestRotSolver(st, bot_num=0):
    bot = st.bots[bot_num]
    collectBoosters(st, bot_num)
    while True:
        path = pathfinder.bfsFind(st, bot.pos,
                                  wrapP(st),
                                  availP=drillableP(st))
        if st.boosters[Booster.DRILL] > 0 and bot.drill_duration <= 0:
            path2 = pathfinder.bfsFind(st, bot.pos,
                                       wrapP(st),
                                       availP=withDrillP(st))
            if path2 is not None and len(path2) < len(path):
                # print("Attach DRILL at " + str(len(bot.actions)))
                st.nextAction(AttachDrill())
                path = path2
        if path is None:
            break
        pathToCommands(path, st)
        if st.boosters[Booster.WHEEL] > 0 and bot.wheel_duration <= 0:
            if random.random() > WHEELS_PROC:
                # print("Attach WHEELS at " + str(len(bot.actions)))
                st.nextAction(AttachWheels())
        if st.boosters[Booster.DRILL] > 0 and bot.drill_duration <= 0:
            if random.random() > DRILL_PROC:
                # print("Attach DRILL at " + str(len(bot.actions)))
                st.nextAction(AttachDrill())
    return st


def numCleaned(st, pos, botnum):
    bot = st.bots[botnum]
    num = 0

    def inc():
        nonlocal num
        num += 1

    bot.repaintWith(pos, st, lambda x, y: inc())
    return num


def closestRotInBlob(st, blob=None, blobRanks=None):
    if blob is None:
        path = pathfinder.bfsFindClosest(st, st.botPos(),
                                         wrapP(st),
                                         rank=lambda x, y:
                                         -numCleaned(st, (x, y), 0))
    else:
        path = pathfinder.bfsFindClosest(
            st, st.botPos(),
            wrapP(st),
            availP=lambda x, y: (x, y) in blob,
            rank=lambda x, y:
            (blobRanks.get((x, y)) or 99999,
             -numCleaned(st, (x, y), 0)))
    if path is None:
        return None
    pathToCommands(path, st)
    return path[len(path) - 1]


def blobClosestRotSolver(st):
    blobs = pathfinder.blobSplit(st, 100000)

    def findBlob(pos):
        for blob in blobs:
            if pos in blob:
                return blob
        return None

    def optimizeBlob():
        for i in range(len(blobs)):
            if (len(blobs[i]) < 10):
                pos = next(iter(blobs[i]))
                otherPath = pathfinder.bfsFind(st, pos,
                                               lambda l, x, y:
                                               st.cell(x, y)[1] == Cell.ROT
                                               and (x, y) not
                                               in blobs[i])
                if otherPath is None:
                    return False
                otherPos = otherPath[len(otherPath) - 1]
                otherBlob = findBlob(otherPos)
                blobs[i] = otherBlob.union(blobs[i])
                blobs.remove(otherBlob)
                return True
        return False

    for it in range(1000):
        optimizeBlob()
    return solveWithBlobs(st, blobs)


# solve('/home/myth/projects/fluffy-engine/desc/prob-047.desc', '/home/myth/projects/fluffy-engine/sol/sol-047.sol', blobClosestRotSolver)


def solveWithBlobs(st, blobs):
    bot = st.bots[0]
    collectBoosters(st, bot)

    def findBlob(pos):
        for blob in blobs:
            if pos in blob:
                return blob
        return None

    curPos = st.botPos()
    while True:
        blob = findBlob(curPos)
        if blob is None:
            break
        blobRanks = {}

        def add(l, x, y):
            blobRanks[(x, y)] = l

        pathfinder.bfsFind(st, curPos,
                           lambda l, x, y: False,
                           register=add)
        while True:
            nextPos = closestRotInBlob(st, blob, {})
            if nextPos is None:
                break
        curPos = closestRotInBlob(st)
        if curPos is None:
            break
    return st.actions()


def split_into_regions(st):
    all_points = []
    ids_yx = [[0]*st.width for _ in range(st.height)]

    def is_obstacle(x, y):
        return st.cell(x, y)[1] is Cell.OBSTACLE

    for y in range(st.height):
        for x in range(st.width):
            if not is_obstacle(x, y):
                all_points.append([x, y])

    X = np.array(all_points)
    k = math.ceil(len(all_points) / 300)
    print(k)

    # TODO: post-process clusters to avoid non-connected groups
    #       merge very small clusters with neighbors
    kmeans = sklearn.cluster.KMeans(n_clusters=k,
                                    random_state=0).fit(X)

    labels = kmeans.labels_
    max_label = 0
    for p, l in zip(all_points, labels):
        l += 1
        ids_yx[p[1]][p[0]] = l
        if l > max_label:
            max_label = l

    id_to_ds = {}
    def merge_if(cond, x, y, x1, y1):
        _id = ids_yx[y][x]
        if _id == 0 or not cond:
            return
        if _id not in id_to_ds:
            id_to_ds[_id] = disjoint_set.DisjointSet()
        if ids_yx[y1][x1] == _id:
            id_to_ds[_id].union((x,y), (x1,y1))
        else:
            id_to_ds[_id].union((x,y), (x,y))

    for y in range(st.height):
        for x in range(st.width):
            merge_if(x>0, x, y, x-1, y)
            merge_if(y>0, x, y, x, y-1)

    for ds in id_to_ds.values():
        sets = list(ds.itersets())
        if len(sets) > 1:
            for s in sets[1:]:
                max_label += 1
                for x, y in s:
                    ids_yx[y][x] = max_label

    # merging small regions

    MIN_SIZE = 20
    id_to_blob = ids_yx_to_blobs_map(ids_yx)

    # collect candidates
    ids_to_merge = []
    for _id, blob in id_to_blob.items():
        if len(blob) < MIN_SIZE:
            ids_to_merge.append(_id)

    nmap = make_region_neighbours_map(ids_yx)

    while len(ids_to_merge) > 0:
        b = ids_to_merge.pop()
        if len(id_to_blob[b]) >= MIN_SIZE:
            continue
        links = nmap[b]
        if len(links) == 0:
            continue
        # will link with a
        a = next(iter(links))

        # bn -- b neighbour
        for bn in nmap[b]:
            nmap[bn].remove(b)
            if bn != a:
                nmap[bn].add(a)
                nmap[a].add(bn)

        # transfer points from b blob to a blob
        for bp in id_to_blob[b]:
            id_to_blob[a].add(bp)

        del nmap[b]
        del id_to_blob[b]

    for _id, blob in id_to_blob.items():
        for x, y in blob:
            ids_yx[y][x] = _id

    return ids_yx



def remove_if_present(_set, _item):
    if _item in _set:
        _set.remove(_item)

def make_region_neighbours_map(ids_yx):
    id_to_neighbours_map = {}

    def ensure_set(a):
        if a == 0:
            return
        if a not in id_to_neighbours_map:
            id_to_neighbours_map[a] = set()

    def link(a, b):
        if a == 0:
            return
        if b == 0:
            return
        if a == b:
            return
        id_to_neighbours_map[a].add(b)
        id_to_neighbours_map[b].add(a)

    h = len(ids_yx)
    w = len(ids_yx[0])
    for y in range(h):
        for x in range(w):
            ensure_set(ids_yx[y][x])
            if x > 0: link(ids_yx[y][x-1], ids_yx[y][x])
            if y > 0: link(ids_yx[y-1][x], ids_yx[y][x])

    return id_to_neighbours_map


def make_traversal_plan_postman(region_ids_yx, initial_id):
    id_to_neighbours_map = make_region_neighbours_map(region_ids_yx)

    G = nx.Graph()

    # TODO: use distances between centroids as weights
    for a, links in id_to_neighbours_map.items():
        for b in links:
            G.add_edge(a, b, weight=1)

    G_min = nx.algorithms.minimum_spanning_tree(G)

    with tempfile.NamedTemporaryFile(mode="w") as edges_csv:
        w = csv.writer(edges_csv)
        w.writerow(["node1", "node2", "trail", "distance"])
        i = 0
        for a, b in G_min.edges():
            w.writerow([str(a), str(b), str(i), 1])
            i += 1
        edges_csv.flush()

        tour, _ = postman_problems.solver.cpp(edges_csv.name,
                                              start_node=str(initial_id))

    # TODO: try post-processing plan to by adding edges from origina
    # graph?
    return list(map(lambda x: int(x[0]), tour))


def make_traversal_plan(region_ids_yx, initial_id):
    id_to_neighbours_map = make_region_neighbours_map(region_ids_yx)

    G = nx.Graph()

    for a, links in id_to_neighbours_map.items():
        for b in links:
            G.add_edge(a, b, weight=1)

    #TODO: initial_id would be considered as root, and thus travsed last
    return list(nx.dfs_postorder_nodes(G, source=initial_id))


def draw_regions(st, ids_yx, traversal_plan, svg_file):
    svg = svgwrite.Drawing(filename=svg_file)
    svg.viewbox(minx=0, miny=0, width=st.width*5, height=st.height*5)
    id_to_color = {}
    def id_color(i):
        if i in id_to_color:
            return id_to_color[i]
        color = svg_colors.random_color(["black", "white"])
        id_to_color[i] = color
        return color

    id_to_coord = {}

    for y in range(st.height):
        for x in range(st.width):
            color = "white"
            cell_kind = st.cell(x, y)[1]
            if cell_kind is Cell.OBSTACLE:
                color = "black"

            cell_id = ids_yx[y][x]
            if cell_id != 0 and color != "black":
                color = id_color(cell_id)
                if cell_id not in id_to_coord:
                    id_to_coord[cell_id] = (x*5+2,y*5+2)

            svg.add(svg.rect(
                insert=(x*5, y*5),
                size=(5,5),
                fill=color,
                stroke="black",
                stroke_width="0.5"))

            if cell_id != 0:
                svg.add(svg.text(str(cell_id), insert=(x*5+1, y*5+4), font_size=3))

    traversal_coords = list(map(lambda x: id_to_coord[x], traversal_plan))

    if len(traversal_coords) > 0:
        svg_traversal_line = svg.polyline(
            points=traversal_coords,
            stroke="red",
            stroke_width="1",
            fill_opacity="0"
        )
        svg.add(svg_traversal_line)

    svg.save()

def draw_regions_for_task(task_file, svg_file):
    st = State.decode(decode.parse_task(task_file))
    bot_pos = st.botPos()
    ids_yx = split_into_regions(st)
    initial_id = ids_yx[bot_pos[1]][bot_pos[0]]
    traversal_plan = make_traversal_plan(ids_yx, initial_id)
    print(list(traversal_plan))
    draw_regions(st, ids_yx, traversal_plan, svg_file)

def ids_yx_to_blobs_map(ids_yx):
    h = len(ids_yx)
    w = len(ids_yx[0])
    id_to_blob = {}
    for y in range(h):
        for x in range(w):
            _id = ids_yx[y][x]
            if _id != 0:
                if not _id in id_to_blob:
                    id_to_blob[_id] = set()
                id_to_blob[_id].add((x,y))
    return id_to_blob

# This should be A* or some pre-computed routing!!
def move_to_blob(st, blob):
    path = pathfinder.bfsFindClosest(
        st,
        st.botPos(),
        lambda l, x, y: (x,y) in blob
    )
    assert path
    pathToCommands(path, st)
    return path[len(path) - 1]


def closestRotInBlob2(st, blob=None):
    if blob is None:
        path = pathfinder.bfsFindClosest(st, st.botPos(),
                                         wrapP(st),
                                         rank=lambda x, y:
                                         -numCleaned(st, (x, y), 0))
    else:
        path = pathfinder.bfsFindClosest(
            st, st.botPos(),
            lambda l, x, y: st.cell(x, y)[1] == Cell.ROT and (x, y) in blob)
    if path is None:
        return None
    pathToCommands(path, st)
    return path[len(path) - 1]


def solve_with_regions(st, qmap_fname):
    qmap = {}
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
    bot = st.bots[0]
    collect_boosters2(st, 0)
    curPos = st.botPos()

    ids_yx = split_into_regions(st)
    id_to_blob = ids_yx_to_blobs_map(ids_yx)
    initial_id = ids_yx[curPos[1]][curPos[0]]
    assert initial_id != 0
    plan = make_traversal_plan(ids_yx, initial_id)
    print(list(plan))
    processed = set()

    blob_points = 0
    for blob_id in plan:
        blob = id_to_blob[blob_id]
        assert blob
        #curPos = move_to_blob(st, blob)
        if blob_id not in processed:
            processed.add(blob_id)
            blob_points += len(blob)
            from q import learning_run1_in_region
            st = learning_run1_in_region(
                qmap, st, blob, at_end_go_to=lambda l, x, y: st.cell(x, y)[1] == Cell.ROT)

            # # TODO: use mcts inside regions to allow rotations
            # while True:
            #     nextPos = closestRotInBlob2(st, blob)
            #     if nextPos is None:
            #         break

    print("blob points", blob_points)
    total_points = 0
    clean_points = 0
    for y in range(st.height):
        for x in range(st.width):
            kind = st.cell(x, y)[1]
            if kind is Cell.CLEAN:
                clean_points += 1
            if kind is not Cell.OBSTACLE:
                total_points += 1
    print("total_points", total_points)
    print("clean_points", clean_points)

    with open(qmap_fname, "wb") as f:
        print("Dumping", qmap_fname, "with ",
              str(round(qmap["count of observations"] * 1e-6, 1)) + "M",
              "observations")
        pickle.dump(qmap, f)
    return st


problem = "/home/theihor/repo/fluffy-engine/desc/prob-002.desc"
draw_regions_for_task(problem, "/home/theihor/repo/fluffy-engine/1.svg")
solve(problem, "/home/theihor/repo/fluffy-engine/q-sol/002.sol",
      lambda s: solve_with_regions(s, '../qmaps/regions.pickle'),
      add_score=False)
