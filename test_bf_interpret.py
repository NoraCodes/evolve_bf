from evolve_bf import interpret
import unittest


class TestBFInterpret(unittest.TestCase):
    def test_output(self):
        hello_world = "++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>."
        result = interpret.evaluate(hello_world, "")
        self.assertEqual(result, "Hello World!\n")

    def test_input(self):
        cat = ",[.,]"
        cat_input = "This is both the input and the output."
        result = interpret.evaluate(cat, cat_input)
        self.assertEqual(result, cat_input)

    def test_timeout(self):
        infinite_loop = "+[]"
        with self.assertRaises(interpret.TimeoutAbortException):
            # This should raise an exception for running too long
            interpret.evaluate(infinite_loop, "")