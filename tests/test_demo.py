import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import unittest
from demo import Profile, discover

class DiscoveryTests(unittest.TestCase):
    def test_filters_deduplicates(self):
        data=[Profile("x",2000,"creative review"),Profile("x",2000,"creative review"),
              Profile("y",900,"review"),Profile("z",4000,"unrelated")]
        self.assertEqual([x["code"] for x in discover(data)],["x"])

if __name__ == "__main__":
    unittest.main()
