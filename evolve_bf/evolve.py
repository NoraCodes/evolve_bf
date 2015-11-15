from evolve_bf import interpret
# This program evolves BF code, and may eventually be improved to evolve BrainFork or 4Brain as well.
# Example: evolve_bf_program(['1', '2'], ['Hello, world!', '!dlrow ,olleH']) will evolve a program which, given 1 as
#   an input, prints Hello, world! and, given 2 as an input, prints the reverse.

from collections import namedtuple
from random import shuffle, choice, randint
from evolve_bf import cost

MappedProgram = namedtuple("MappedProgram", ["cost", "program"])
ProgramReport = namedtuple("ProgramReport", ["program", "cost", "generations", "output"])
EvolveOptions = namedtuple("EvolveOptions", ['cull_ratio', 'population_size', 'initial_program_size',
                                             'program_timeout', 'generation_limit', 'verbose', 'cost_options'])

default_evolve_options = EvolveOptions(cull_ratio = 0.5, population_size = 100, initial_program_size = 8,
                                       program_timeout = 10, generation_limit = 10000, verbose=False,
                                       cost_options=cost.default_cost_options)

valid_commands = ['.', ',', '[', ']', '<', '>', '+', '-']  # These are the valid commands in BF which will be used to
                                                           # evolve our programs
valid_commands_no_end_loop = ['.', ',', '[', '<', '>', '+', '-']
valid_commands_no_loops = ['.', ',', '<', '>', '+', '-']


def get_key_for_MappedProgram(mapped_program):
    return mapped_program.cost


def evolve_bf_program(inputs, targets, options = default_evolve_options):
    """
    Use the genetic algorithm to create a BF program that, given each input, computes the corresponding output.
    :param inputs: A list of inputs which produce a corresponding output
    :param targets: A list of outputs corresponding to inputs
    :param cull_ratio: What proportion of each generation should we kill? .5 induces no growth, while values less than
            .5 kill fewer, meaning that the population grows, and values greater than it kill more,
    :param population_size: The initial size of the population (P_0). May grow or shrink depending on other inputs
    :param initial_program_size: How long programs start out as being
    :param program_timeout: How long each organism may run for, ms
    :param generation_limit: How many generations to run for before giving up
    :param verbose: Print on every generation, or no?
    """

    # Check the inputs and outputs for nonstrings, convert them to strings

    # Generate an initial population

    current_population = generate_population(options.population_size, options.initial_program_size)
    # This is population P_0 and, at the beginning, P_g as well.
    interstitial_population = [] # This is I, the mutated but non-crossed generation
    new_population = []  # P_g+1

    generations = 0  # This is g

    winner = ProgramReport("",0,0,"")

    while True:
        # Test that we have not run over
        if generations >= options.generation_limit:
            return None
        # Test the cost of each member of P_g
        #print(current_population)
        cost_mapping = []
        for program_index in range(0, len(current_population)):
            cost_mapping.append(MappedProgram(cost=cost.cost_function(inputs, targets,
                                                                        current_population[program_index],
                                                                        options=options.cost_options),
                                              program=current_population[program_index]))
            # In this way, cost_mapping[0] is (cost_of_P_g[0], P_g[0])

            # Test this program has a cost of zero; if so, return. We are done.
            if cost_mapping[program_index].cost == 0:
                winner_output = "\n"
                for input_string_index in range(0, len(inputs)):
                    winner_output += "{}:{}\n".format(inputs[input_string_index],
                                                      interpret.evaluate(cost_mapping[program_index].program,
                                                                            inputs[input_string_index]))
                winner = ProgramReport(program = cost_mapping[program_index].program,
                                       cost = cost_mapping[program_index].cost,
                                       generations = generations,
                                       output = winner_output)
                return winner  # There is a winner, so break out of the loop

        # Sort the cost mapping to prepare for culling
        sorted_cost_mapping = sorted(cost_mapping, key=get_key_for_MappedProgram)

        if options.verbose:
            # Report on the current winner:
            print("Gen. {}: Cost {} \n{}\n{}\n".format(generations, sorted_cost_mapping[0].cost,
                                                       sorted_cost_mapping[0].program,
                                                       interpret.evaluate(sorted_cost_mapping[0].program,
                                                                             inputs[0])))

        # Kill cull_ratio of P_g, starting with those with the largest cost, removing cost mappings in the process
        center_number = int(len(sorted_cost_mapping) * options.cull_ratio)
        culled_population = [mapped_program.program for mapped_program in sorted_cost_mapping[:center_number]]
        # Explaination: loop through sorted_cost_mapping, stripping cost mappings, until we hit center_number.
        # The rest are killed.
        #print(cost_mapping)
        #print(culled_population)
        # Replicate-with-errors from P_g to I
        interstitial_population = [mutation_function(program, looping_chance=1) for program in culled_population]
        #print(interstitial_population)

        # Cross P_g with I, creating P_g+1
        shuffle(culled_population)
        shuffle(interstitial_population)
        for population_index in range(0, len(culled_population)):
            #print(population_index, len(culled_population), len(interstitial_population))
            n, nprime = crossing_function(culled_population[population_index],
                                              interstitial_population[population_index])
            new_population.append(n)
            new_population.append(nprime)

        # g = g+1
        current_population = new_population
        interstitial_population = []
        new_population = []
        generations += 1

    return winner


def generate_population(individuals, length=10):
    i = 0
    population = []
    while i < individuals:
        individual = ""
        program_index = 0
        while program_index < length:
            # Randomly choose a symbol
            next_command = choice(valid_commands_no_end_loop)
            if next_command == '[':  # We're starting a new loop
                if length - program_index <= 3:
                    # No room for a loop.
                    next_command = choice(valid_commands_no_loops)
                else:
                    individual += '['   # Start the loop; adding this to program_index is handled by the outer while
                                        #  (it thinks this is all  one char)
                    inside_loop_length = randint(1, length - (program_index+1)) #  i+1 to leave room for ]
                    j = 0
                    while j < inside_loop_length:
                        individual += choice(valid_commands_no_loops)
                        j += 1
                    # Close off the loop
                    individual += ']'
                    program_index += inside_loop_length + 1  # The 1 is for the closing ']'
            else:
                individual += next_command
            program_index += 1
        i += 1
        population.append(individual)
    return population


def mutation_function(program, likelihood_of_inplace = 100, likelihood_of_addition= 30,
                      liklihood_of_deletion= 40, liklihood_of_none = 1, looping_chance = 20):
    """
    Mutate program based on liklihood inputs
    :param program:  The program to mutate
    :param likelihood_of_inplace: How common an in-place mutation is (e.g. . -> ,)
    :param likelihood_of_addition: How common an addition mutation is
    :param liklihood_of_deletion: How common a deletion is
    :param liklihood_of_none: How common perfect transcription is
    :param looping_chance: How likley it is to insert a loop. Percent.
    :return: A new program
    """
    choice_list = ['inplace'] * likelihood_of_inplace + \
        ['addition'] * likelihood_of_addition + \
        ['deletion'] * liklihood_of_deletion + \
        ['none'] * liklihood_of_none
    mutation_type = choice(choice_list)  # Pick a mutation type

    if len(program) <= 1:
        # The mutation logic does not work on one-length programs
        return program + choice(valid_commands_no_loops)

    if mutation_type == 'inplace':
        index_to_mutate = randint(1, len(program))
        # Replace a single symbol
        # TODO: Implement adding loops by this mechanism
        # Implementaion note: when inserting a [, insert a ] at (pos_of_[) + (random_int_less_than_length)
        if program[index_to_mutate - 1] in ['[', ']']:  # -1 here because indices are from 0 not from 1
            # If the symbol is part of a loop, figure out how to replace it safely.
            # TODO: MAKE THIS WORK!
            # For now we just chicken out
            pass
        else:
            do_add_loop = choice([True] * looping_chance + [False] * (100-looping_chance))
            if do_add_loop:
                if index_to_mutate < len(program) - 2:
                    # We have enough room
                    skip_index = index_to_mutate + randint(1, len(program) - index_to_mutate)
                    program = program[:index_to_mutate] + '[' + program[index_to_mutate:skip_index] + ']' + \
                              program[skip_index:]
                else:
                    # Not enough room
                    pass
            else:
                program = program[:(index_to_mutate - 1)] + choice(valid_commands_no_loops) + program[index_to_mutate:]
                pass
    if mutation_type == 'addition':
        index_to_mutate = randint(1, len(program))
        # Insert a symbol at index_to_mutate
        do_add_loop = choice([True] * looping_chance + [False] * (100-looping_chance))
        if do_add_loop:
            if index_to_mutate < len(program) - 2:
                # We have enough room
                skip_index = index_to_mutate + randint(1, len(program) - index_to_mutate)
                program = program[:index_to_mutate] + '[' + program[index_to_mutate:skip_index] + ']' + \
                          program[skip_index:]
            else:
                # Not enough room
                pass
        else:
            program = program[:index_to_mutate] + choice(valid_commands_no_loops) + program[index_to_mutate:]
        pass
    if mutation_type == 'deletion':
        index_to_mutate = randint(1, len(program))
        if program[index_to_mutate - 1] in ['[', ']']:  # -1 here because indices are from 0 not from 1
            # If the symbol is part of a loop, count up to the next one and delete that too
            next_bracket_position = index_to_mutate - 1
            for char in program[index_to_mutate:]:
                next_bracket_position += 1
                if char == ']':
                    break
            program = program[:(index_to_mutate - 1)] + program[index_to_mutate:]
            program = program[:(next_bracket_position - 1)] + program[next_bracket_position:]
        else:
            # Delete a single symbol
            program = program[:(index_to_mutate - 1)] + program[index_to_mutate:]
            pass
    if mutation_type == 'none':
        # No mutation
        pass
    return program


def crossing_function(program_a, program_b):
    """
    Cross program_a and program_b, producing program_ab and program_ab'
    :param program_a: Program A for the cross
    :param program_b: Program B for the cross
    :return:
    """
    # TODO: Implement something other than naive randomness here
    if len(program_a) == 1 or len(program_b) == 1:
        return program_a + program_b, program_b + program_a

    if len(program_a) > len(program_b):
        crossing_index = randint(0, len(program_b))
    else:
        crossing_index = randint(0, len(program_a))
    program_aprime = program_a[:crossing_index] + program_b[crossing_index:]
    program_bprime = program_b[:crossing_index] + program_a[crossing_index:]
    return program_aprime, program_bprime


def report_evolution(results):
    """
    Present a ProgramReport in a readable way
    :param results: the ProgramReport
    :return: bool
    """
    if results is None:
        return False
    else:
        print("Success!\nGeneration {}:\n\t{}\ngiving:{}".format(results.generations, results.program, results.output))
        return True
