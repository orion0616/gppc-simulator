import simulator
import numpy as np
from PIL import Image
import unittest

class TestSimulator(unittest.TestCase):
    def test_convert_points(self):
        line = "(90,192)(90,191)(90,190)(90,189)(90,188)(89,188)(88,188)(87,188)"
        expected = [[90,192],[90,191],[90,190],[90,189],
                    [90,188],[89,188],[88,188],[87,188]]
        self.assertEqual(simulator.convert_points(line), expected)

    def test_upsize_image_ok(self):
        image = Image.fromarray(np.uint8([[[255,255,255],[0,0,0],[1,1,1]],[[3,3,3],[4,4,4],[5,5,5]]]), "RGB")
        doubled = np.uint8([[[255,255,255],[255,255,255],[0,0,0],[0,0,0],[1,1,1],[1,1,1]],
                             [[255,255,255],[255,255,255],[0,0,0],[0,0,0],[1,1,1],[1,1,1]],
                             [[3,3,3],[3,3,3],[4,4,4],[4,4,4],[5,5,5],[5,5,5]],
                             [[3,3,3],[3,3,3],[4,4,4],[4,4,4],[5,5,5],[5,5,5]]])
        expected = Image.fromarray(doubled, "RGB")
        self.assertEqual(simulator.upsize_image(image), expected)

    def test_upsize_image_ng(self):
        expected = image = Image.fromarray(np.uint8(np.zeros(1200*800*3).reshape(1200,800,3)), "RGB")
        self.assertEqual(simulator.upsize_image(image), expected)

if __name__ == "__main__":
    unittest.main()
