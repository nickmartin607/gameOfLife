#!/usr/bin/env python

# Conway's Game of Life
#
# Nick Martin (njm5722)
# Authentication & Security Models, RIT Fall 2016

from math import ceil
from subprocess import check_output
from random import randint
from argparse import ArgumentParser, ArgumentTypeError

INITIAL_SETUPS = {
    'blinker': {
        'width': 5,
        'height': 5,
        'coordinates': [(2,1), (2,2), (2,3)]
    },
    'glider': {
        'width': 10,
        'height': 10,
        'coordinates': [(1,3), (2,3), (3,3), (3,2), (2,1)]
    },
    'toad': {
        'width': 6,
        'height': 6,
        'coordinates': [(1,3), (2,3), (3,3), (2,2), (3,2), (4,2)]
    },
    'lwss': {
        'width': 20,
        'height': 5,
        'coordinates': [(0,0), (0,2), (3,0), (4,1), (4,2), (4,3), (3,3), (2,3), (1,3)]
    },
    'exploder': {
        'width': 15,
        'height': 15,
        'coordinates': [(5,5), (5,6), (5,7), (5,8), (5,9), (9,5), (9,6), (9,7), (9,8), (9,9), (7,5), (7,9)]
    },
    'tumbler': {
        'width': 11,
        'height': 9,
        'coordinates': [(1,3), (1,2), (2,1), (3,2), (4,3), (3,4), (3,5), (4,5), (6,5), (7,5), (7,4), (6,3), (7,2), (8,1), (9,2), (9,3)]
    }
}


class Grid():
    def __init__(self, width, height, coordinates):
        self.width, self.height = width, height
        self.cell_count = 0
        self.generations = 0
        self.grid = [[0 for _ in xrange(width)] for _ in xrange(height)]
        self.old_grid = []

        for x, y in coordinates:
            self.fill_cell(x, y)

    # Get the value of a cell, current grid by default
    def get_cell(self, x, y, old=False):
        g = self.old_grid if old else self.grid
        return g[y][x]

        # Mark a cell as 'Alive'
    def fill_cell(self, x, y):
        if not self.get_cell(x, y):
            self.cell_count += 1
        self.grid[y][x] = 1

    # Mark a cell as 'Dead'
    def clear_cell(self, x, y):
        if self.get_cell(x, y):
            self.cell_count -= 1
        self.grid[y][x] = 0

    # Total up neighbors for a given cell
    def regenerate(self, x, y):
        neighbors = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        count = 0
        for X, Y in neighbors:
            if 0 <= x + X < self.width and 0 <= y + Y < self.height:
                if self.get_cell(x + X, y + Y, old=True):
                    count += 1
    
        # Adjust cell status for next generation
        cell = self.get_cell(x, y, old=True)
        if (count in (2, 3) and cell) or (count == 3 and not cell):
            self.fill_cell(x, y)
        else:
            self.clear_cell(x, y)

  
class Board():
    def __init__(self, width, height):
        self.width, self.height = width + 2, height + 2
        self.term_width = int(check_output(['tput', 'cols']))
        self.display_space = 6
        self.horiz_bar = '+{}+'.format('-' * width)

    # Build 2D List represnting board display
    def build_board(self, grid):
        display = []
        display.append(
            '{:^{w}}'.format("Gen #{}".format(grid.generations), w=self.width))
        display.append(self.horiz_bar)
        for y in xrange(grid.height):
            row = []
            for x in xrange(grid.width):
                row.append('#' if grid.get_cell(x, y) else ' ')
            display.append('|{}|'.format(''.join(row)))
        display.append(self.horiz_bar)
        return display

    # Build string representing entire game
    def build_display(self, results):
        display = ''

        cols = self.term_width / (self.width + self.display_space)
        rows = int(ceil(len(results) / float(cols)))
        for row in [results[i:i + cols] for i in xrange(0, len(results), cols)]:
            display += '\n'
            for board_row in xrange(self.height + 1):
                display += '{}\n'.format(
                    str(' ' * self.display_space).join(
                        [row[gen][board_row] for gen in xrange(len(row))]))
        return display
    
  
  
def main(setup):
    # Generate Grid and Board objects
    g = Grid(setup['width'], setup['height'], setup['coordinates'])
    b = Board(setup['width'], setup['height'])

    # Perform generations on the board
    results = []
    while g.generations <= args.rounds and g.cell_count:
        # Build grid display and add to output
        results.append(b.build_board(g))

        # Increment generation counter, and create duplicate board to reference
        g.generations += 1
        g.old_grid = [row[:] for row in g.grid]

        # Loop over each cell in the board
        for x in xrange(g.width):
            for y in xrange(g.height):
                g.regenerate(x, y)

    # Print final game results
    print b.build_display(results)

# Coordinate type specification for coordinate arguments
def coordinate(c):
    try:
        return c.split(',')
        # x, y = map(int, c.split(','))
        # return x, y
    except:
        raise ArgumentTypeError("Coordinates must be (x,y)")

if __name__ == '__main__':
    parser = ArgumentParser(usage='%(prog)s [options]', description="Conway's Game of Life")

    # Arguments for initial board setups
    setup = parser.add_argument_group("Optional Game Initial Setup Options")
    setup.add_argument('--initial', dest='setup', choices=INITIAL_SETUPS.keys(), help="Initial configuration")
    setup.add_argument('--coordinates', nargs='+', help="Specific coordinates for custom initial setup") #type=coordinate,

    # Arguments for game specifications
    specs = parser.add_argument_group("Optional Game Specification")
    specs.add_argument('-d', '--dimension', dest='dim', type=int, default=10, metavar="#", help="Dimension of the boards width and height")
    specs.add_argument('-c', '--cells', type=int, default=20, metavar="#", help="Number of default active cells")
    specs.add_argument('-r', '--rounds', type=int, default=10, metavar="#", help="Number of generations to run for")

    # Read arguments from command line
    args = parser.parse_args()
    
    # Verify specified starting number of cells dont exceed board capacity
    if args.cells > args.dim**2:
        parser.error("Number of initial cells exceeds maximum board capacity")

    if args.setup:
        main(INITIAL_SETUPS[args.setup])
    else:
        if args.coordinates:
            coordinates = []
            for coordinate_pair in args.coordinates:
                print coordinate_pair
                x, y = coordinate_pair.split(',')
                coordinates.append((int(x), int(y)))
                if int(x) >= args.dim or int(y) >= args.dim:
                    parser.error("Coordinates out of range of board dimensions")
        else:   # Random Configuration
            coordinates = []
            while len(coordinates) < args.cells:
                x, y = randint(0, args.dim - 1), randint(0, args.dim - 1)
                if (x, y) not in coordinates:
                    coordinates.append((x, y))
        main({'width': args.dim, 'height': args.dim, 'coordinates': coordinates})
