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
    results = evolve_bf_program(['Hello, world!', 'Flump', 'Alawakkawumpwump'],
                            ['Hello, world!', 'Flump', 'Alawakkawumpwump'])

    # add two numbers seperated by a \0x00
    #results = evolve_bf_program([string.ascii_letters], ['Hello, world!'], verbose=True)

    report_evolution(results)