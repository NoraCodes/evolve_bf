#!/usr/bin/env python3
from evolve_bf.evolve import *

if __name__ == "__main__":

    cost_options = cost.default_cost_options._replace(ascii_only=True)

    evolve_options = default_evolve_options._replace(cost_options=cost_options, verbose=True)
    # Using _replace allows us to set only the values we actually care about.

    results = supervised_evolve(['Hello, world!', 'Flump.'], ['Hello, world!', 'Flump.'], evolve_options)

    results = supervised_evolve(['ABCDEFGHIJKLMNOPQRSTUVWXYZ'], ['abcdefghijklmnopqrstuvwxyz'], evolve_options)
