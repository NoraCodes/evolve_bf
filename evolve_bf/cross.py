from random import randint

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
