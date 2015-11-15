# Interpret the BF language
# BF Interpreter for evolve_bf
# Based on code created 2011 Sebastian Kaspari
# Modified for in-program evaluation 2015 Leo Tindall

import time

class TimeoutAbortException(Exception):
    pass

class BFSyntaxException(Exception):
    pass


def buildbracemap(code):
    temp_bracestack, bracemap = [], {}

    for position, command in enumerate(code):
        if command == "[":
            temp_bracestack.append(position)
        if command == "]":
            try:
                start = temp_bracestack.pop()
            except:
                raise BFSyntaxException("Loop close without loop open at {}.".format(position))
            bracemap[start] = position
            bracemap[position] = start
    return bracemap


def cleanup(code):
    return list(filter(lambda x: x in ['.', ',', '[', ']', '<', '>', '+', '-'], code))


def evaluate(code, input_string, timeout = 5):
    code     = cleanup(list(code))
    bracemap = buildbracemap(code)

    cells, codeptr, cellptr, input_index = [0], 0, 0, 0
    output = ""
    input_string += chr(0)  # Add a terminator; programs like cat can break if this is not done.

    time_begin = time.time() # We count from here for the timeout
    time_target = time_begin + (timeout / 1000)  # Convert from milliseconds

    while codeptr < len(code):
        if time.time() > time_target:
            # We have spent too long in this execution. Using an exception avoids the problem that Igliu had:
            #   https://igliu.com/program-that-writes-brainfuck/
            #   in which his code would loop infinitely to produce a 0 return value (his abort value)
            raise TimeoutAbortException("Your BF code timed out (ran for too long)." +
                                        " The timeout value was {} ms. Consider raising the" +
                                        " timeout by passing timeout={} to evaluate().".format(timeout, timeout+10))

        command = code[codeptr]

        if command == ">":
          cellptr += 1
        if cellptr == len(cells): cells.append(0)

        if command == "<":
            cellptr = 0 if cellptr <= 0 else cellptr - 1

        if command == "+":
            cells[cellptr] = cells[cellptr] + 1 if cells[cellptr] < 255 else 0

        if command == "-":
            cells[cellptr] = cells[cellptr] - 1 if cells[cellptr] > 0 else 255

        if command == "[" and cells[cellptr] == 0:
            codeptr = bracemap[codeptr]
        if command == "]" and cells[cellptr] != 0:
            codeptr = bracemap[codeptr]
        if command == ".":
            output += chr(cells[cellptr])
        if command == ",":
            try:
                cells[cellptr] = ord(input_string[input_index])
            except IndexError:
                # Tried to read past the last char of input, get 0
                cells[cellptr] = 0
            input_index += 1

        codeptr += 1

    return output

