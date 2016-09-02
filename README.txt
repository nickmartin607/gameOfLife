usage: gameOfLife.py [options]

Conway's Game of Life

optional arguments:
  -h, --help            show this help message and exit

Optional Game Initial Setup Options:
  --initial {blinker,toad,lwss,tumbler,glider,exploder}
                        Initial configuration
  --coordinates COORDINATES [COORDINATES ...]
                        Specific coordinates for custom initial setup

Optional Game Specification:
  -d #, --dimension #   Dimension of the boards width and height
  -c #, --cells #       Number of default active cells
  -r #, --rounds #      Number of generations to run for
