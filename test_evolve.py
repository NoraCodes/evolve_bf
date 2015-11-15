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

    cost_table = {'timeout': 50,
                  'no output': 25,
                  'non_ascii': 1,
                  'too_short': 5,
                  'too_long': 1,
                  'one_char_wrong': 5,
                  'extra_char': 3,
                  'missing_char': 2,
                  'non_intersection': 1,
                  'not_equal': 1}

    cost_options = cost.CostOptions(program_timeout=10,
                                   cost_table=cost_table,
                                   ascii_only=True)

    evolve_options = EvolveOptions(cull_ratio = 0.5,
                                   population_size = 100,
                                   initial_program_size = 8,
                                   program_timeout = 10,
                                   generation_limit = 10000,
                                   verbose=True,
                                   cost_options=cost_options)

    results = evolve_bf_program(['Hello, world!'], ['!dlrow ,olleH'], evolve_options)

    report_evolution(results)