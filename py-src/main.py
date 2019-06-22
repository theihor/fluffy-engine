import sys
import solver


def main():
    desc = sys.argv[1]
    sol = sys.argv[2]
    solver.solve(desc, sol, solver.closestRotSolver)


if __name__ == '__main__':
    main()
