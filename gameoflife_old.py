#!/usr/bin/env python

# Nick Martin (njm5722)
# Authentication & Security Models, RIT Fall 2016

from subprocess import check_output
from random import randint
from argparse import ArgumentParser, ArgumentTypeError

ALIVE, DEAD = '# '
BOARD_CORNER, BOARD_HORIZ, BOARD_VERT = '+-|'
BOARD_SPACING = 5
NEIGHBORS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
INITIAL_SETUPS = {
    'blinker': {'dim': 5, 'config': [(2,1),(2,2),(2,3)]},
    'glider': {'dim': 10, 'config': [(1,3),(2,3),(3,3),(3,2),(2,1)]},
    'toad': {'dim': 6, 'config': [(1,3),(2,3),(3,3),(2,2),(3,2),(4,2)]},
    'lwss': {
        'dim': 20, 'config': [
            (0,1),(0,3),(3,1),(4,2),(4,3),(4,4),(3,4),(2,4),(1,4)
        ]
    },
    'exploder': {
        'dim': 15, 'config': [
            (5,5),(5,6),(5,7),(5,8),(5,9),(9,5),(9,6),(9,7),(9,8),(9,9),(7,5),
            (7,9)
        ]
    },
    'tumbler': {
        'dim': 11, 'config': [
            (1,3),(1,2),(2,1),(3,2),(4,3),(3,4),(3,5),(4,5),(6,5),(7,5),(7,4),
            (6,3),(7,2),(8,1),(9,2),(9,3)
        ]
    }
}


class Board():
    def __init__(self, dim):
        self.cell_count = 0
        self.gen = 0
        self.dim = dim
        self.board = [[0 for x in xrange(dim)] for y in xrange(dim)]
    
    # Setup initial board configuration
    def config(self, cells, coords):
        if not coords:
            while len(coords) < cells:
                x, y = randint(0, self.dim - 1), randint(0, self.dim - 1)
                if (x, y) not in coords:
                    coords.append((x, y))
        [self.create(x, y) for x, y in coords]
    
    # Mark a location on the board as 'alive'
    def create(self, x, y):
        if not self.board[y][x]:
            self.cell_count += 1
        self.board[y][x] = 1

    # Mark a location on the board as 'dead'
    def remove(self, x, y):
        if self.board[y][x]:
            self.cell_count -= 1
        self.board[y][x] = 0
    
    # Execute a subsequent generation
    def execute(self):
        # Create duplicate board to reference
        tmp_board = [b[:] for b in self.board]

        # Loop over each cell in the board
        for x in xrange(self.dim):
            for y in xrange(self.dim):
                
                # Count up total neighbors within 1 cell radius
                n = 0
                for X, Y in NEIGHBORS:
                    if 0 <= X + x < self.dim and 0 <= Y + y < self.dim:
                        if tmp_board[Y + y][X + x]:
                            n += 1
        
                # Adjust cell status for next generation
                tmp_cell = tmp_board[y][x]
                if (n in (2, 3) and tmp_cell) or (n == 3 and not tmp_cell):
                    self.create(x, y)
                else:
                    self.remove(x, y)
        
    # Build 2D List represnting board display
    def display(self):
        horiz_bar = '{c}{h}{c}'.format(c=BOARD_CORNER, h=BOARD_HORIZ * self.dim)
        grid = [[ALIVE if c else DEAD for c in r] for r in self.board]
        grid_list = ['|{}|'.format(''.join(r)) for r in grid]
        gen_str = '{:^{w}}'.format(
            'Gen #' + str(self.gen) if self.gen > 0 else 'Initial',
            w=len(horiz_bar))
        return [gen_str, horiz_bar] + grid_list + [horiz_bar]
        
       
def main(args):
    dim = INITIAL_SETUPS[args.setup]['dim'] if args.setup else args.dim
    coords = INITIAL_SETUPS[args.setup]['config'] if args.setup else []
    
    # Generate Board object, and setup initial configuration
    board = Board(dim)
    board.config(args.cells, coords)
    
    # Perform generations on the board
    results = []
    for generation in xrange(args.rounds + 1):
        results.append(board.display())
        board.execute()
        board.gen += 1
        
        # Stop game if no live cells remain
        if not board.cell_count:
            break
        
    board_height, board_width = len(results[0]), len(results[0][0])
    row_max = int(check_output(['tput','cols'])) / (board_width + BOARD_SPACING)
    rows = [results[i:i + row_max] for i in xrange(0, board.gen, row_max)]

    # Print Boards
    output = ''
    for output_row in xrange(len(rows)):
        row = rows[output_row]
        output += '\n'
        for board_row in xrange(board_height):
            output_row = [row[g][board_row] for g in xrange(len(row))]
            output += '{}\n'.format(str(' ' * BOARD_SPACING).join(output_row))
    print(output)


# Coordinate type specification for coordinate arguments
def coordinate(coord_str):
    try:
        x, y = map(int, coord_str.split(','))
        return x, y
    except:
        raise ArgumentTypeError("Coordinates must be (x,y)")


if __name__ == '__main__':
    parser = ArgumentParser(usage='%(prog)s [options]',
        description="Conway's Game of Life")
    
    # Arguments for initial board setups
    setup = parser.add_argument_group("Optional Game Initial Setup Options")
    setup.add_argument('--initial', dest='setup',
        choices=INITIAL_SETUPS.keys(), help="Initial configuration")
    setup.add_argument('--coordinates', dest='coords', type=coordinate,
        nargs='+', help="Specific coordinates for custom initial setup")
    
    # Arguments for game specifications
    specs = parser.add_argument_group("Optional Game Specification")
    specs.add_argument('-d', '--dimension', dest='dim', type=int, default=10,
        metavar="#", help="Dimension of the boards width and height")
    specs.add_argument('-c', '--cells', type=int, default=20, metavar="#",
        help="Number of default active cells")
    specs.add_argument('-r', '--rounds', type=int, default=10, metavar="#",
        help="Number of generations to run for")
    
    # Read arguments from command line
    args = parser.parse_args()
    
    # Verify custom coordinates dont exceed board dimensions
    if args.coords:
        for x,y in args.coords:
            if x >= args.dim or y >= args.dim:
                parser.error("Coordinates out of range of board dimensions")
                
    # Verify specified starting number of cells dont exceed board capacity
    if args.cells > args.dim**2:
        parser.error("Number of initial cells exceeds maximum board capacity")
    
    main(args)
