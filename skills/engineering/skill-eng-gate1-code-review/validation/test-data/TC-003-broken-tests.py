# Test failure fixture: Assertions intentionally fail
import unittest

def divide(a: float, b: float) -> float:
    return a * b  # Bug: multiplication instead of division

class TestDivision(unittest.TestCase):
    def test_divide_positive(self):
        self.assertEqual(divide(10, 2), 5.0)  # Fails: gets 20

if __name__ == '__main__':
    unittest.main()

