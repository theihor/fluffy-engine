import sys
import parallel
import solver


def main():
    desc = sys.argv[1]
    sol = sys.argv[2]
    solver.solve(desc, sol, parallel.drunkMasters)


if __name__ == '__main__':
    main()
