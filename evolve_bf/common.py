valid_commands = ['.', ',', '[', ']', '<', '>', '+', '-']  # These are the valid commands in BF which will be used to
                                                           # evolve our programs
valid_commands_no_end_loop = ['.', ',', '[', '<', '>', '+', '-']
valid_commands_no_loops = ['.', ',', '<', '>', '+', '-']
valid_commands_no_loops_weighted = ['.', ',', '<', '>'] + (['+'] * 10) + (['-'] * 10)
