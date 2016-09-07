#!/usr/bin/env python

# Conway's Game of Life
#
# Nick Martin (njm5722)
# Authentication & Security Models, RIT Fall 2016

from itertools import product
from subprocess import check_output
from random import randint
from argparse import ArgumentParser
from pprint import pprint

SPACE_BETWEEN_BOARDS = 3
INITIAL_SETUPS = {
    'blinker': {'width': 5, 'height': 5, 'coordinates': [(2,1), (2,2), (2,3)]},
    'glider': {'width': 10, 'height': 10, 'coordinates': [(1,3), (2,3), (3,3), (3,2), (2,1)]},
    'toad': {'width': 6, 'height': 6, 'coordinates': [(1,3), (2,3), (3,3), (2,2), (3,2), (4,2)]},
    'lwss': {'width': 20, 'height': 5, 'coordinates': [(0,0), (0,2), (3,0), (4,1), (4,2), (4,3), (3,3), (2,3), (1,3)]},
    'exploder': {'width': 15, 'height': 15, 'coordinates': [(5,5), (5,6), (5,7), (5,8), (5,9), (9,5), (9,6), (9,7), (9,8), (9,9), (7,5), (7,9)]},
    'tumbler': {'width': 11, 'height': 9, 'coordinates': [(1,3), (1,2), (2,1), (3,2), (4,3), (3,4), (3,5), (4,5), (6,5), (7,5), (7,4), (6,3), (7,2), (8,1), (9,2), (9,3)]}
}
class Game(object):
    def __init__(self, rows, cols, coordinates):
        self.rows = rows
        self.cols = cols
        self.grid = [[[0 for _ in range(cols)] for _ in range(rows)]]
        for col, row in coordinates:
            self.set_cell(row, col, 0, 1)
    
    # Assign a cell in a given generation a value
    def set_cell(self, row, col, gen, value):
        self.grid[gen][row][col] = value
        
    # Get the value of a cell in a given generation
    def get_cell(self, row, col, gen):
        return self.grid[gen][row][col]

    # Get the number of live cells in a given generation
    def cell_count(self, gen):
        return sum([sum(row) for row in self.grid[gen]])
        
    # Get the number of generations
    def current_gen(self):
        return len(self.grid) - 1
        
    # Duplicate the grid for a new generation
    def add_generation(self):
        self.grid.append([row[:] for row in self.grid[self.current_gen()]])

    def count_neighbors(self, row, col, gen):
        count = 0
        neighbors = [(row + r, col + c) for r, c in product(range(-1, 2), range(-1, 2)) if (r, c) != (0,0)]
        for row, col in neighbors:
            if row in range(self.rows) and col in range(self.cols):
                if self.get_cell(row, col, gen):
                    count += 1
        return count
        
    # Adjust a cell for a new generation
    def update_cells(self, gen):
        for row, col in product(range(self.rows), range(self.cols)):
            count = self.count_neighbors(row, col, gen)
            prior_cell = self.get_cell(row, col, gen)
            if (count in (2, 3) and prior_cell) or (count == 3 and not prior_cell):
                val = 1
            else:
                val = 0
            self.set_cell(row, col, gen + 1, val)
            
    def to_array(self):
        output = []
        for gen in range(self.current_gen() + 1):
            display = ['{:^{w}}'.format("Gen{}".format(gen), w=self.cols + 2)]
            display.append('+{}+'.format('-' * self.cols))
            for row in range(self.rows):
                grid_row = []
                for col in range(self.cols):
                    grid_row.append('#' if self.get_cell(row, col, gen) else ' ')
                display.append('|{}|'.format(''.join(grid_row)))
            display.append('+{}+'.format('-' * self.cols))
            output.append(display)
        return output
        
    def to_string(self):
        display = ''
        display_cols = int(check_output(['tput', 'cols'])) / (self.cols + 2 + SPACE_BETWEEN_BOARDS)
        output = self.to_array()
        for row in [output[i:i + display_cols] for i in range(0, len(self.grid), display_cols)]:
            for grid_row in range(self.rows + 2 + 1):
                display += '\n{}'.format(str(' ' * SPACE_BETWEEN_BOARDS).join([row[gen][grid_row] for gen in range(len(row))]))
            display += '\n'
        
        return display

def main(args):
    max_rounds = args.rounds
    if args.setup:
        rows = INITIAL_SETUPS[args.setup]['height']
        cols = INITIAL_SETUPS[args.setup]['width']
        coords = INITIAL_SETUPS[args.setup]['coordinates']
    else:
        rows = args.dim
        cols = args.dim
        if args.coordinates:
            coords = [[int(i) for i in pair.split(',')] for pair in args.coordinates]
        else:   # Random Configuration
            coords = set()
            while len(coords) < args.cells:
                coords.add((randint(0, cols - 1), randint(0, rows - 1)))
    
    game = Game(rows, cols, list(coords))

    for gen in range(max_rounds):
        if not game.cell_count(gen):
            break
        game.add_generation()
        game.update_cells(gen)
        
    display = game.to_string()
    print display

def parse_arguments():
    parser = ArgumentParser(usage='%(prog)s [options]', description="Conway's Game of Life")
    parser_setup = parser.add_argument_group("Optional Game Initial Setup Options")
    parser_specs = parser.add_argument_group("Optional Game Specification")
    parser_setup.add_argument('--initial', dest='setup', choices=INITIAL_SETUPS.keys(), help="Initial configuration")
    parser_setup.add_argument('--coordinates', nargs='+', help="Specific coordinates for custom initial setup") #type=coordinate,
    parser_specs.add_argument('-d', '--dimension', dest='dim', type=int, default=10, metavar="#", help="Dimension of the boards width and height")
    parser_specs.add_argument('-c', '--cells', type=int, default=20, metavar="#", help="Number of default active cells")
    parser_specs.add_argument('-r', '--rounds', type=int, default=10, metavar="#", help="Number of generations to run for")
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
    main(parse_arguments())
    
