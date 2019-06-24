import sys
import parallel
import solver
import q


def main():
    desc = sys.argv[1]
    sol = sys.argv[2]
    solver.solve(desc, sol, parallel.drunkMasters)


def qmain():
    desc = sys.argv[1]
    sol = sys.argv[2]

    qmap = sys.argv[3]
    solver.solve(desc, sol, lambda state: q.run_qbot(state, qmap))


if __name__ == '__main__':
    qmain()
