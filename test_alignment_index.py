import math
import unittest

from alignment_index import (PAPER_PAIRS, classify, cosine, coverage,
                             global_index, pair_alignment)


class TestPaperValues(unittest.TestCase):
    def test_pairwise_scores_match_table4(self):
        expected = [(0.85, 0.62, 0.53), (0.81, 0.50, 0.41), (0.67, 0.38, 0.25)]
        for p, (cs, kp, a) in zip(PAPER_PAIRS, expected):
            self.assertAlmostEqual(cosine(p.c, p.r), cs, places=2)
            self.assertAlmostEqual(coverage(p.c, p.r), kp, delta=0.006)
            self.assertAlmostEqual(pair_alignment(p.c, p.r), a, places=2)

    def test_global_index_eq4(self):
        self.assertAlmostEqual(global_index(PAPER_PAIRS), 0.4163, places=4)
        self.assertEqual(classify(global_index(PAPER_PAIRS)), "Medium")

    def test_equal_weights_sensitivity(self):
        a = global_index(PAPER_PAIRS, weights=[1 / 3] * 3)
        self.assertAlmostEqual(a, 0.395, places=3)
        self.assertEqual(classify(a), "Low")

    def test_cosine_only(self):
        self.assertAlmostEqual(global_index(PAPER_PAIRS, use_cosine_only=True),
                               0.79, places=2)


class TestProperties(unittest.TestCase):
    def test_perfect_alignment_when_c_is_multiple_of_r(self):
        r = (1, 2, 1, 2, 1)
        c = (2, 4, 2, 4, 2)          # c = 2r, lambda >= 1
        self.assertAlmostEqual(pair_alignment(c, r), 1.0)

    def test_bounds(self):
        a = pair_alignment((5, 0, 0, 0, 0), (0, 5, 0, 0, 0))
        self.assertTrue(0.0 <= a <= 1.0)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            cosine((0, 0, 0, 0, 0), (1, 1, 1, 1, 1))
        with self.assertRaises(ValueError):
            cosine((6, 0, 0, 0, 0), (1, 1, 1, 1, 1))
        with self.assertRaises(ValueError):
            global_index(PAPER_PAIRS, weights=[0.5, 0.5, 0.5])

    def test_levels(self):
        self.assertEqual(classify(0.39), "Low")
        self.assertEqual(classify(0.40), "Medium")
        self.assertEqual(classify(0.70), "Medium")
        self.assertEqual(classify(0.71), "High")


if __name__ == "__main__":
    unittest.main()
