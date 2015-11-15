from collections import namedtuple
from evolve_bf import interpret
import string

ascii_list = string.ascii_letters+string.digits

# What each failure costs
default_cost_table = {'timeout': 50,
                      'no output': 25,
                      'non_ascii': 1,
                      'too_short': 5,
                      'too_long': 1,
                      'one_char_wrong': 5,
                      'extra_char': 3,
                      'missing_char': 2,
                      'non_intersection': 1,
                      'not_equal': 1}

# Options for the cost_function:
#   program_timeout: The maximum time each BF program is allowed, in ms
#   cost_table: a dict containing the values required for costing, one int per key
#   ascii_only: True means that non-alphanumeric-ASCII output characters add to the cost
CostOptions = namedtuple("CostOptions", ['program_timeout', 'cost_table', 'ascii_only'])

default_cost_options = CostOptions(program_timeout=10,
                                   cost_table=default_cost_table,
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
    for input_string_index in range(0, len(inputs)):
        program_cost_addition = 0
        # Run the program, ensuring that it is not an infinite loop or a syntax error, then applying costs to it
        try:
            output = interpret.evaluate(program, inputs[input_string_index], options.program_timeout)
        except interpret.TimeoutAbortException:
            program_cost_addition += options.cost_table['timeout']
            program_cost += program_cost_addition
            continue # This is to prevent output being reffed after, since it is not assigned if the try fails
        except interpret.BFSyntaxException:
            program_cost_addition = 2^30 - 1  # Max int: syntax errors are inviable
            program_cost += program_cost_addition
            continue
        except KeyError:
            program_cost_addition = 2^30 - 1  # Max int; syntax errors are inviable
            program_cost += program_cost_addition
            continue

        if output == targets[input_string_index]:
            program_cost_addition = 0  # Ding ding ding we have a winner
            program_cost += program_cost_addition
            continue
        else:
            program_cost_addition += options.cost_table['not_equal']

        if output == '':
            # There's no output.
            program_cost_addition += options.cost_table['no output']
            program_cost += program_cost_addition
            continue  # Prevent double jeopardy
        else:
            # There is output, and it's not right.
            if len(output) > len(targets[input_string_index]):
                program_cost_addition += options.cost_table['too_long'] * (len(output) - len(targets[input_string_index]))
            elif len(output) < len(targets[input_string_index]):
                program_cost_addition += options.cost_table['too_short'] * (len(targets[input_string_index]) - len(output))

            if targets[input_string_index] in output:
                # Our desired output is in the output, penalize only for the extra chars
                program_cost_addition += (len(output) - len(targets[input_string_index])) * options.cost_table['extra_char']
            elif output in targets[input_string_index]:
                # We have an incomplete output, penalize only for those missing chars
                program_cost_addition += (len(targets[input_string_index]) - len(output)) * options.cost_table['missing_char']
            else:
                # Just find the intersection as sets, as a last ditch differentiator
                intersection = set_intersection(targets[input_string_index], output)
                program_cost_addition += len(output) - len(intersection)

            if options.ascii_only: # Skip this if we don't need it; it's SLOW
                for character in output:
                    if character not in ascii_list:
                        # non-ascii chars
                        # TODO: Allow turning this off
                        program_cost_addition += options.cost_table['non_ascii']

        program_cost += program_cost_addition

    return program_cost
