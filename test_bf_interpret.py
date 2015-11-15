from evolve_bf import bf_interpret
import unittest


class TestBFInterpret(unittest.TestCase):
    def test_output(self):
        hello_world = "++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>."
        result = bf_interpret.evaluate(hello_world, "")
        self.assertEqual(result, "Hello World!\n")

    def test_input(self):
        cat = ",[.,]"
        cat_input = "This is both the input and the output."
        result = bf_interpret.evaluate(cat, cat_input)
        self.assertEqual(result, cat_input)

    def test_timeout(self):
        infinite_loop = "+[]"
        with self.assertRaises(bf_interpret.TimeoutAbortException):
            # This should raise an exception for running too long
            bf_interpret.evaluate(infinite_loop, "")