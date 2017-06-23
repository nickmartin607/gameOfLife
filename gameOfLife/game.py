from itertools import product
from subprocess import check_output

""" 
    Conway's Game of Life
    Nick Martin (njm5722)
    Authentication & Security Models, RIT Fall 2016 
"""

SPACE_BETWEEN_BOARDS = 2
NEIGHBOR_OFFSETS = [
    (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)
]


class Game(object):
    """ Object representing Conway's Game of Life """

    def __init__(self, **kwargs):
        """ Function to initialize a Game object """
        self.rows = kwargs.get('rows')
        self.cols = kwargs.get('cols')
        self.wrap = kwargs.get('wrap')

        self.grid = [[[0 for _ in range(self.cols)] for _ in range(self.rows)]]
        for col, row in kwargs.get('coords'):
            self.set_cell(row, col, state=1, gen=0)


    def __repr__(self):
        """ Get a string containing the entire game to be printed to stdout """
        horiz_edge = '+{}+'.format('-' * self.cols)
        term_width = int(check_output(['tput', 'cols']))
        disp_cols = term_width / (self.cols + 2 + SPACE_BETWEEN_BOARDS)

        output = []
        for gen in range(len(self.grid)):
            g = [horiz_edge, horiz_edge]
            for row in self.grid[gen]:
                r = "|{}|".format(''.join(["#" if col else " " for col in row]))
                g.insert(-1, r)
            title = '{:^{w}}'.format("Gen{}".format(gen), w=self.cols + 2)
            g.insert(0, title)

            output.append(g)
        
        disp = ''
        for disp_row in range(0, len(self.grid), disp_cols):
            for output_row in [output[disp_row:disp_row + disp_cols]]:
                for grid_row in range(self.rows + 2 + 1):
                    disp += '\n ' + str(' ' * SPACE_BETWEEN_BOARDS).join(
                        [output_row[gen][grid_row] for gen in range(len(output_row))])
            disp += '\n'
        return disp


    def get_curr_generation(self):
        """ Get the index of the most recent generation """
        return len(self.grid) - 1


    def add_generation(self):
        """ Duplicate the grid for a new generation """
        prior_gen = [row[:] for row in self.grid[self.get_curr_generation()]]
        self.grid.append(prior_gen)


    def set_cell(self, row, col, state, gen):
        """ Assign a cell in a given generation a value """
        self.grid[gen][row][col] = state


    def get_cell(self, row, col, gen):
        """ Get the value of a cell in a given generation """
        # row, col = self.wrap_coordinates(row, col)
        try:
            return self.grid[gen][row][col]
        except:
            return 0


    def get_cell_count(self, gen):
        """ Get the number of live cells in a given generation """
        return sum(map(sum, self.grid[gen]))


    def update_cells(self, gen):
        """ Adjust a cell for a new generation """
        for row, col in product(range(self.rows), range(self.cols)):
            neighbors = [self.wrap_coordinates(row + r, col + c) for r, c in NEIGHBOR_OFFSETS]
            count = sum([self.get_cell(r, c, gen) for r, c in neighbors])
            curr_state = self.get_cell(row, col, gen)
            if curr_state and count in (2, 3):
                new_state = 1
            elif not curr_state and count in (3,):
                new_state = 1
            else:
                new_state = 0
            if curr_state is not new_state:
                self.set_cell(row, col, new_state, gen + 1)


    def wrap_coordinates(self, row, col):
        """ Adjust coordinates if wrapping is enabled, and extend past
            current limits """
        if self.wrap:
            if row >= self.rows:
                row -= self.rows
            elif row < 0:
                row += self.rows
            if col >= self.cols:
                col -= self.cols
            elif col < 0:
                col += self.cols
        return (row, col)

    def run(self, generations):
        for gen in range(generations):
            if not self.get_cell_count(gen):
                break
            self.add_generation()
            self.update_cells(gen)

        print self

