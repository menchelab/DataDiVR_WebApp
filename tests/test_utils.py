import unittest
from app.utils import hex_to_rgb, hex_to_rgba

class TestUtils(unittest.TestCase):
    
    def test_hex_to_rgb(self):
        self.assertEqual(hex_to_rgb("#FFFFFF"), [255, 255, 255])
        self.assertEqual(hex_to_rgb("#000000"), [0, 0, 0])
        self.assertEqual(hex_to_rgb("#FF5733"), [255, 87, 51])

    def test_hex_to_rgba(self):
        self.assertEqual(hex_to_rgba("#FFFFFFFF"), (255, 255, 255, 255))
        self.assertEqual(hex_to_rgba("#000000FF"), (0, 0, 0, 255))

if __name__ == "__main__":
    unittest.main()
