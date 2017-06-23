from argparse import ArgumentParser
from random import randint
from gameOfLife.configs import Configurations
from gameOfLife.game import Game

""" 
	Conway's Game of Life
    Nick Martin (njm5722)
    Authentication & Security Models, RIT Fall 2016 
        Updated June 2017
"""


def parse_arguments():
    """ Parse the arguments supplied from the command line """
    p = ArgumentParser(usage='%(prog)s [options]', 
        description="Conway's Game of Life")
    p_setup = p.add_argument_group("Optional Game Initial Setup Options")
    p_specs = p.add_argument_group("Optional Game Specification")
    
    p_setup.add_argument('--initial', dest='setup', choices=Configurations.keys(), 
        help="Initial configuration")
    p_setup.add_argument('--coordinates', dest='coords', metavar="(X,Y)", 
        nargs='+', help="Specific coordinates for custom initial setup")
    p_specs.add_argument('-d', '--dimension', dest='dim', type=int, default=10, 
        metavar="#", help="Dimension of the boards width and height")
    p_specs.add_argument('-c', '--cells', type=int, default=20, metavar="#", 
        help="Number of default active cells")
    p_specs.add_argument('-g', '--generations', type=int, default=10, metavar="#", 
        help="Number of generations to run for")
    p_specs.add_argument('-w', '--wrap', action="store_true", 
        help="Wrap edges of grid")
    args = p.parse_args()
    
    # Verify specified starting number of cells dont exceed board capacity
    if args.cells > args.dim**2:
        p.error("Number of initial cells exceeds maximum board capacity")

    # Verify coordinates, if given, are within board dimensions
    if args.coords:
        for pair in args.coords:
            col, row = pair.split(',')
            if int(col) not in range(args.dim) or int(row) not in range(args.dim):
                p.error("Coordinates out of range of board dimensions [{}x{}]".format(args.dim, args.dim))

    # Set Initial Coordinates, either from a configuration or from the supplied pairs
    if args.setup:
        setattr(args, 'coords', Configurations[args.setup]['coords'])
        setattr(args, 'rows', Configurations[args.setup]['rows'])
        setattr(args, 'cols', Configurations[args.setup]['cols'])
    else:
        if args.coords:
            coords = [[int(i) for i in pair.split(',')] for pair in args.coords]
        else:   # Random Configuration
            coords = set()
            while len(coords) < args.cells:
                coords.add((randint(0, args.dim - 1), randint(0, args.dim - 1)))
        setattr(args, 'coords', coords)
        setattr(args, 'rows', args.dim)
        setattr(args, 'cols', args.dim)

    return vars(args)


if __name__ == '__main__':
    args = parse_arguments()
    game = Game(**args)
    game.run(args.get('generations'))
