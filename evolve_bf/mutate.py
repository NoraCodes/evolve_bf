from random import choice, randint
from evolve_bf import common
from collections import namedtuple

MutateOptions = namedtuple("MutationOptions", ['likelihood_of_inplace', 'likelihood_of_addition',
                                               'likelihood_of_deletion', 'likelihood_of_none',
                                               'looping_chance'])

default_mutate_options = MutateOptions(likelihood_of_inplace = 100, likelihood_of_addition= 30,
                                       likelihood_of_deletion= 40, likelihood_of_none = 1, looping_chance = 20)
# Options for the mutation function:
# likelihood_of_inplace: How common an in-place mutation is (e.g. . -> ,)
# likelihood_of_addition: How common an addition mutation is
# liklihood_of_deletion: How common a deletion is
# liklihood_of_none: How common perfect transcription is
# looping_chance: How likley it is to insert a loop. Percent.


def mutation_function(program, options=default_mutate_options):
    """
    Mutate program based on liklihood inputs
    :param program: The program to mutate
    :param options: A MutateOptions with options for the function
    :return: A new program
    """
    choice_list = ['inplace'] * options.likelihood_of_inplace + \
        ['addition'] * options.likelihood_of_addition + \
        ['deletion'] * options.likelihood_of_deletion + \
        ['none'] * options.likelihood_of_none
    mutation_type = choice(choice_list)  # Pick a mutation type

    if len(program) <= 1:
        # The mutation logic does not work on one-length programs
        return program + choice(common.valid_commands_no_loops)

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
            do_add_loop = choice([True] * options.looping_chance + [False] * (100-options.looping_chance))
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
                program = program[:(index_to_mutate - 1)] + choice(common.valid_commands_no_loops) + \
                          program[index_to_mutate:]
                pass
    if mutation_type == 'addition':
        index_to_mutate = randint(1, len(program))
        # Insert a symbol at index_to_mutate
        do_add_loop = choice([True] * options.looping_chance + [False] * (100-options.looping_chance))
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
            program = program[:index_to_mutate] + choice(common.valid_commands_no_loops) + program[index_to_mutate:]
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