import simulator
import unittest

class TestSimulator(unittest.TestCase):
    def test_convert_points(self):
        line = "(90,192)(90,191)(90,190)(90,189)(90,188)(89,188)(88,188)(87,188)"
        expected = [[90,192],[90,191],[90,190],[90,189],
                    [90,188],[89,188],[88,188],[87,188]]
        self.assertEqual(simulator.convert_points(line), expected)

if __name__ == "__main__":
    unittest.main()
