#!/usr/bin/env python

# Conway's Game of Life
#
# Nick Martin (njm5722)
# Authentication & Security Models, RIT Fall 2016

from math import ceil
from subprocess import check_output
from random import randint
from argparse import ArgumentParser, ArgumentTypeError
from pprint import pprint

SPACE_BETWEEN_BOARDS = 14
NEIGHBORS = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
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
    def update_cell(self, x, y):
        count = 0
        for X, Y in NEIGHBORS:
            if 0 <= x + X < self.width and 0 <= y + Y < self.height:
                if self.get_cell(x + X, y + Y, old=True):
                    count += 1
    
        # Adjust cell status for next generation
        cell = self.get_cell(x, y, old=True)
        if (count in (2, 3) and cell) or (count == 3 and not cell):
            self.fill_cell(x, y)
        else:
            self.clear_cell(x, y)
            
    # Update board for a new generation
    def new_generation(self):
        display = self.build_board()
        
        self.old_grid = [row[:] for row in self.grid]
        self.generations += 1
        for x in xrange(self.width):
            for y in xrange(self.height):
                self.update_cell(x, y)
        return display
            
        
    def build_board(self):
        horiz_bar = '+{}+'.format('-' * self.width)
        display = []
        display.append('{:^{w}}'.format("Gen #{}".format(self.generations), w=self.width + 2))
        display.append(horiz_bar)
        for y in xrange(self.height):
            row = []
            for x in xrange(self.width):
                row.append('#' if self.get_cell(x, y) else ' ')
            display.append('|{}|'.format(''.join(row)))
        display.append(horiz_bar)
        return display

def main(args):
    if args.setup:
        width = INITIAL_SETUPS[args.setup]['width']
        height = INITIAL_SETUPS[args.setup]['height']
        coordinates = INITIAL_SETUPS[args.setup]['coordinates']
    else:
        if args.coordinates:
            coordinates = [[int(i) for i in pair.split(',')] for pair in args.coordinates]
        else:   # Random Configuration
            coordinates = []
            while len(coordinates) < args.cells:
                x, y = randint(0, args.dim - 1), randint(0, args.dim - 1)
                if (x, y) not in coordinates:
                    coordinates.append((x, y))
        width = args.dim
        height = args.dim
    
    # Generate Grid object
    grid = Grid(width, height, coordinates)

    # Perform generations on the board
    results = []
    while grid.generations <= args.rounds and grid.cell_count:
        generation_display = grid.new_generation()
        results.append(generation_display)

    # Print final game results
    display = ''
    terminal_width = int(check_output(['tput', 'cols']))
    display_cols = terminal_width / (grid.width + 2 + SPACE_BETWEEN_BOARDS)
    for row in [results[i:i + display_cols] for i in xrange(0, grid.generations, display_cols)]:
        display += '\n'
        for board_row in xrange(grid.height + 2 + 1):
            display += '{}\n'.format(str(' ' * SPACE_BETWEEN_BOARDS).join([row[gen][board_row] for gen in xrange(len(row))]))
    print display

def parse_arguments():
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

    args = parser.parse_args()

    # Verify specified starting number of cells dont exceed board capacity
    if args.cells > args.dim**2:
        parser.error("Number of initial cells exceeds maximum board capacity")

    # Verify coordinates, if given, are within board dimensions
    if args.coordinates:
        for pair in args.coordinates:
            x, y = pair.split(',')
            if int(x) >= args.dim or int(y) >= args.dim:
                parser.error("Coordinates out of range of board dimensions")
    
    # Read arguments from command line
    return args

if __name__ == '__main__':
    
    args = parse_arguments()
    main(args)
    
