from tuneflow_py.utils import greater_than, greater_equal, lower_than, lower_equal
import unittest


class TestBinarySearch(unittest.TestCase):
    def test_greater_equal(self):
        self.assertEqual(greater_equal([1, 2, 3, 3, 4, 5], 0), 0)
        self.assertEqual(greater_equal([1, 2, 3, 3, 4, 5], 1), 0)
        self.assertEqual(greater_equal([1, 2, 3, 3, 4, 5], 3), 2)
        self.assertEqual(greater_equal([{"val": 1}, {"val": 2}, {"val": 3}, {
                         "val": 3}, {"val": 4}, {"val": 5}], {"val": 3}, key=lambda x: x["val"]), 2)
        self.assertEqual(greater_equal([1, 2, 3, 3, 4, 5], 6), 6)

    def test_greater_than(self):
        self.assertEqual(greater_than([1, 2, 3, 3, 4, 5], 0), 0)
        self.assertEqual(greater_than([1, 2, 3, 3, 4, 5], 1), 1)
        self.assertEqual(greater_than([1, 2, 3, 3, 4, 5], 3), 4)
        self.assertEqual(greater_than([{"val": 1}, {"val": 2}, {"val": 3}, {
                         "val": 3}, {"val": 4}, {"val": 5}], {"val": 3}, key=lambda x: x["val"]), 4)
        self.assertEqual(greater_than([1, 2, 3, 3, 4, 5], 6), 6)

    def test_lower_equal(self):
        self.assertEqual(lower_equal([1, 2, 3, 3, 4, 5], 0), -1)
        self.assertEqual(lower_equal([1, 2, 3, 3, 4, 5], 1), 0)
        self.assertEqual(lower_equal([1, 2, 3, 3, 4, 5], 3), 3)
        self.assertEqual(lower_equal([{"val": 1}, {"val": 2}, {"val": 3}, {
                         "val": 3}, {"val": 4}, {"val": 5}], {"val": 3}, key=lambda x: x["val"]), 3)
        self.assertEqual(lower_equal([1, 2, 3, 3, 4, 5], 6), 5)

    def test_lower_than(self):
        self.assertEqual(lower_than([1, 2, 3, 3, 4, 5], 0), -1)
        self.assertEqual(lower_than([1, 2, 3, 3, 4, 5], 1), -1)
        self.assertEqual(lower_than([1, 2, 3, 3, 4, 5], 3), 1)
        self.assertEqual(lower_than([{"val": 1}, {"val": 2}, {"val": 3}, {
                         "val": 3}, {"val": 4}, {"val": 5}], {"val": 3}, key=lambda x: x["val"]), 1)
        self.assertEqual(lower_than([1, 2, 3, 3, 4, 5], 6), 5)


if __name__ == '__main__':
    unittest.main()
