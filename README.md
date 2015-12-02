# evolve_bf
A program for evolving BF code given a list of inputs and their corresponding outputs.

### Usage

In the simplest form, we can evolve a Hello, world! program with one line (not counting imports).

```
from evolve_bf.evolve import supervised_evolve

# Input: none
# Output: Hello, world!
supervised_evolve([''], ['Hello, world!'])
```

Or, for somewhat more advanced usage:

```
from evolve_bf.evolve import *

# Set verbose mode, but otherwise use the defaults
evolve_options = default_evolve_options._replace(verbose=True)

# Define a spec for adding A to an input string
inputs  = ['',  'Hello, world!',  'Foo']
outputs = ['A', 'Hello, world!A', 'FooA']

supervised_evolve(inputs, outputs, evolve_options)
```

### Options

All options are carried in namedtuples.

```
# in evolve_bf.evolve
default_evolve_options = EvolveOptions(
                                       cull_ratio = 0.5,  # Out of 1, how many of the weakest per generation to kill.
                                       population_size = 1000,  # The size of the population. Enforced after crossing.
                                       initial_program_size = 8,  # The length of the programs created for the initial population.
                                       program_timeout = 20,  # How many milliseconds a program can run before being declared inviable
                                       generation_limit = 10000,  # How many generations to run before giving up
                                       verbose = False,  # Whether to print reports every generation. Useful during development.
                                       cost_options = cost.default_cost_options,  # For advanced users only
                                       mutate_options = mutate.default_mutate_options  # For advanced users only
                                      )
```

## How it Works

### The short version
The program generates a set of organisms in BF and evaluates them, using the difference between the inputs and expected outputs to assign a 'cost' to each organism. It then takes the 'best', those with the lowest cost, and mutates them, then crosses the mutated versions with the non-mutated ones. Then it evaluates those, mutates and crosses those, et cetera. Eventually, a program that satisfies the criteria is found, and its cost is 0. That's the result.
