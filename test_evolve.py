__author__ = 'leo'

from evolve_bf.evolve import *

if __name__ == "__main__":

    # Test the generator
    #for program in generate_population(10, 200):
    #    print(program)
    #    try:
    #        print("\t" + bf_interpret.evaluate(program, "lmao", timeout=10))
    #    except bf_interpret.TimeoutAbortException:
    #        print("\tTimed out.")

    # Test the mutator
    #program = generate_population(1, 100)[0]
    #i = 0
    #while i < 100:
    #    program = mutation_function(program)
    #    print('\n' + program)
    #    try:
    #        print("\t" + bf_interpret.evaluate(program, "lmao", timeout=10))
    #    except bf_interpret.TimeoutAbortException:
    #        print("\tTimed out.")
    #    except bf_interpret.BFSyntaxException:
    #        print("Mutation broke syntax, this is BAD.")
    #        exit(1)
    #    i += 1


    #print(evolve_bf_program(['1', '2'], ['Hello, world!', '!dlrow ,olleH']))
    # simple cat spec
    #results = evolve_bf_program(['Hello, world!', 'Flump', 'Alawakkawumpwump'],
    #                        ['Hello, world!', 'Flump', 'Alawakkawumpwump'])

    cost_options = cost.default_cost_options._replace(ascii_only=True)

    evolve_options = default_evolve_options._replace(cost_options=cost_options, verbose=True)
    # Using _replace allows us to set only the values we actually care about.

    results = supervised_evolve(['Hello, world!'], ['Hello, fool.'], evolve_options)