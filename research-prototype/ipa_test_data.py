"""
Write IPA data for testing
"""
import argparse
from random import randrange
from pathlib import Path
import sys
from csv import reader

def get_args(args):

    parser = argparse.ArgumentParser(
        description = "Generate random IPA input data for MP-SPDZ")
    parser.add_argument("data", type = str,
                        help = "Name of data file")
    parser.add_argument("--numrows_power", type = int, default = 12,
                        help = "Power of 2 of # of inputs")
    parser.add_argument("--randomize", type = int, default = 0,
                        nargs = '?',
                        help = "Fill out with random data")
    parser.add_argument("--modpower", type = int, default = 32,
                        help = "Power of the modulus")

    return parser.parse_args(args)

def process(fname: str,
            numrows_power: int,
            modulus: int = 2 ** 31,
            mkmod: int = 2 ** 8,
            breakdown_keys: int = 4,
            randomize : bool = False):

    lines = 0
    with open(Path(fname + '.csv'), 'r') as fil:
        for line in reader(fil):
            lines += 1
            yield line
    numrows = 2 ** numrows_power

    data = ((randrange(modulus) for _ in range(lines, numrows))
            if randomize
            else (0 for _ in range(lines,numrows)))
    
    yield from (map(str,[_,0,0,0]) for _ in data)

def main():

    args = get_args(sys.argv[1: ])

    player_data = Path('Player-Data')
    player_data.mkdir(parents = True, exist_ok = True)

    with open(player_data / 'Input-P0-0', 'w') as fil:
        fil.write('\n'.join((' '.join(_)
                             for _ in process(args.data,
                                              args.numrows_power,
                                              modulus = 2 ** args.modpower,
                                              randomize = args.randomize != 0))))
        

main()
