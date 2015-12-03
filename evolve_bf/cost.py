from collections import namedtuple
from evolve_bf import interpret
import string
ascii_list = string.ascii_letters+string.digits

MAX_CODEPOINT = 1114111  # The maximum Unicode codepoint

# What each failure costs
default_cost_table = {'timeout': 1,
                      'no output': 25,
                      'non_ascii': 1,
                      'too_short': 5,
                      'too_long': 4,
                      'one_char_wrong': 5,
                      'extra_char': 4,
                      'missing_char': 4,
                      'wrong_char': 1, # NOTE: this is n times abs(ord(target) - ord(actual))
                      'non_intersection': 1,
                      'not_equal': 1}

# Options for the cost_function:
#   program_timeout: The maximum time each BF program is allowed, in ms
#   cost_table: a dict containing the values required for costing, one int per key
#   ascii_only: True means that non-alphanumeric-ASCII output characters add to the cost
CostOptions = namedtuple("CostOptions", ['program_timeout', 'cost_table', 'time_cost', 'ascii_only'])

default_cost_options = CostOptions(program_timeout=10,
                                   cost_table=default_cost_table,
                                   time_cost = False,
                                   ascii_only=True)

def set_intersection(a, b):
    c = []
    for e in a:
        if e in b:
            c.append(e)
    return c


def cost_function(inputs, targets, program, options=default_cost_options):
    """
    Check whether a given program, when passed inputs, produces the corresponding outputs
    :param inputs: Inputs to pass
    :param targets: Expected targets
    :param options: A CostOptions namedtuple containing all options for cost function execution
    :return: int
    """
    program_cost = 0
    program_cost_addition = 0
    time_cost = 0
    for input_string_index in range(0, len(inputs)):
        program_cost_addition = 0
        # Run the program, ensuring that it is not an infinite loop or a syntax error, then applying costs to it
        try:
            (output, runtime) = interpret.evaluate(program, inputs[input_string_index], options.program_timeout, return_time=True)
        except (interpret.BFSyntaxException, KeyError, interpret.TimeoutAbortException):
            # Program was not valid - mismatched brackets
            return False
        if options.time_cost:
            time_cost += int(runtime * 1000)  # This will only be added to the cost if the program is not correct, i.e., the cost is not zero at the end.
        else:
            time_cost = 0

        if output == targets[input_string_index]:
            # Program output is CORRECT for this input
            program_cost_addition = 0  # Ding ding ding we have a winner
            program_cost += program_cost_addition
            continue
        else:
            # This is here to ensure that incorrect programs cannot win unless someone changes the value :(
            program_cost_addition += options.cost_table['not_equal']

        # Now, apply the simple cost value.
        if len(output) == 0:
            # No output - penalize at maximum for all expected chars
            program_cost_addition += options.cost_table['wrong_char'] * MAX_CODEPOINT * len(targets[input_string_index])
        elif len(output) < len(targets[input_string_index]):
            # Missing some chars. Penalize for the difference between existing chars and target, then
            #    for missing chars.
            for char_index in range(0, len(output)):
                # output is shorter, so this is safe
                expected_char = targets[input_string_index][char_index]
                actual_char = output[char_index]
                program_cost_addition += options.cost_table['wrong_char'] * abs(ord(expected_char) - ord(actual_char))
            program_cost_addition += options.cost_table['wrong_char'] * MAX_CODEPOINT * \
                    abs(len(output) - len(targets[input_string_index]))
        elif len(targets[input_string_index]) < len(output):
            # Too many chars; penalize for the difference between existing chars and target, then
            #   for missing chars.
            for char_index in range(0, len(targets[input_string_index])):
                # target is shorter, so this is safe
                expected_char = targets[input_string_index][char_index]
                actual_char = output[char_index]
                program_cost_addition += options.cost_table['wrong_char'] * abs(ord(expected_char) - ord(actual_char))
            for char in output[len(targets[input_string_index]):]:
                program_cost_addition += options.cost_table['wrong_char'] * ord(char)
        else:
            # They are of equal lengths; just compare them.
            for char_index in range(0, len(targets[input_string_index])):
                # target is as long as output, so this is safe
                expected_char = targets[input_string_index][char_index]
                actual_char = output[char_index]
                program_cost_addition += options.cost_table['wrong_char'] * abs(ord(expected_char) - ord(actual_char))
        program_cost += program_cost_addition 

    if program_cost > 0:
        program_cost += time_cost
        return program_cost
    else:
        return program_cost

def old_cost_function(inputs, targets, program, options=default_cost_options):
    """
    Check whether a given program, when passed inputs, produces the corresponding outputs
    :param inputs: Inputs to pass
    :param targets: Expected targets
    :param options: A CostOptions namedtuple containing all options for cost function execution
    :return: int
    """
    program_cost = 0
    program_cost_addition = 0
    for input_string_index in range(0, len(inputs)):
        program_cost_addition = 0
        # Run the program, ensuring that it is not an infinite loop or a syntax error, then applying costs to it
        try:
            output = interpret.evaluate(program, inputs[input_string_index], options.program_timeout)
        except interpret.TimeoutAbortException:
            # Program ran for too long
            program_cost_addition += options.cost_table['timeout']
            program_cost += program_cost_addition
            continue # This is to prevent output being reffed after, since it is not assigned if the try fails
        except (interpret.BFSyntaxException, KeyError):
            # Program was not valid - mismatched brackets
            return False
        if output == targets[input_string_index]:
            # Program output is CORRECT for this input
            program_cost_addition = 0  # Ding ding ding we have a winner
            program_cost += program_cost_addition
            continue
        else:
            # This is here to ensure that incorrect programs cannot win unless someone changes the value :(
            program_cost_addition += options.cost_table['not_equal']

        if output == '':
            # There's no output.
            program_cost_addition += options.cost_table['no output']
            program_cost += program_cost_addition
            continue  # Prevent double jeopardy
        else:
            # There is output, and it's not right.

            # Find an offset at which a correct character resides, preventing the "y-umlaut problem"
            #   (ýHello, world! instead of Hello, world! creating an evolutionary boundary)
            if len(output) > len(targets[input_string_index]):
                max_offset = len(targets[input_string_index])
            else:
                max_offset = len(output)

            correction_offset = 0
            for char_index in range(0, max_offset):
                if output[correction_offset] == targets[input_string_index][0]:
                    correction_offset = char_index
                    break
            # The correction offset tells us about some wrong chars; penalize for them.
            #program_cost_addition += correction_offset * options.cost_table['wrong_char']
            for char_index in range(correction_offset, len(output)):
                try:
                    program_cost_addition += options.cost_table['wrong_char'] * \
                        abs(ord(output[char_index]) - ord(targets[input_string_index][char_index]))
                except IndexError:
                    # Index out of range, one string is done; abort.
                    break

            divergence_index = False
            if len(output) > len(targets[input_string_index]):
                # Output is longer, so we need to penalize for that as well
                for char_index in range(correction_offset, len(targets[input_string_index])):
                    if output[char_index] != targets[input_string_index][char_index]:
                        # Incorrectness penalty
                        divergence_index = char_index

                if divergence_index is not False:
                    # If there was a divergence, penalize based on incorrect chars within the correct length
                    for char_index in range(divergence_index, len(targets[input_string_index])):
                        # Add penalty per wrong char
                        if output[char_index] != targets[input_string_index][char_index]:
                            program_cost_addition += options.cost_table['wrong_char']

            else:
                # Output is equal or shorter; apply penalty for missing chars and shortness
                if len(output) > 0:
                    for char_index in range(correction_offset, len(output)):
                        if output[char_index] != targets[input_string_index][char_index]:
                            # We've found the divergence point
                            divergence_index = char_index
                        if divergence_index is not False:
                            # There was a divergence; penalize based on incorrect chars within the correct length
                            for char_index in range(divergence_index, len(output)):
                                # Add penalty per wrong char
                                if output[char_index] != targets[input_string_index][char_index]:
                                    program_cost_addition += options.cost_table['wrong_char']

            if len(output) > len(targets[input_string_index]):
                # The output is too long.
                program_cost_addition += options.cost_table['too_long'] * \
                                         (len(output) - len(targets[input_string_index]))
            elif len(output) < len(targets[input_string_index]):
                # The output is too short.
                program_cost_addition += options.cost_table['too_short'] * \
                                         (len(targets[input_string_index]) - len(output))

            if targets[input_string_index] in output:
                # Our desired output is in the output, penalize only for the extra chars
                program_cost_addition += (len(output) - len(targets[input_string_index])) * \
                                         options.cost_table['extra_char']
            elif output in targets[input_string_index]:
                # We have an incomplete output, penalize only for those missing chars
                program_cost_addition += (len(targets[input_string_index]) - len(output)) * \
                                         options.cost_table['missing_char']
            else:
                # Just find the intersection as sets, as a last ditch differentiator
                intersection = set_intersection(targets[input_string_index], output)
                program_cost_addition += len(output) - len(intersection)

            if options.ascii_only: # Skip this if we don't need it; it's SLOW
                for character in output:
                    if character not in ascii_list:
                        # Penalize for non-alphanumeric-ascii chars
                        program_cost_addition += options.cost_table['non_ascii']

        program_cost += program_cost_addition

    return program_cost


