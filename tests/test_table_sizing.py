import unittest
from ui.table_sizing import fit_column_widths


class TableSizingTests(unittest.TestCase):
    def test_catalog_fits_and_reserves_action_width(self):
        preferred = [48, 110, 240, 300, 100, 200]
        minimum = [38, 90, 130, 100, 80, 200]
        widths = fit_column_widths(preferred, minimum, 920, [0, 1, 1, 1, 0, 0])
        self.assertEqual(sum(widths), 920)
        self.assertTrue(all(width >= low for width, low in zip(widths, minimum)))
        self.assertEqual(widths[-1], 200)

    def test_grows_descriptions_not_action_buttons(self):
        self.assertEqual(fit_column_widths([40, 120, 180], [40, 90, 180], 600, [0, 1, 0]),
                         [40, 380, 180])

    def test_scroll_only_when_minimum_content_cannot_fit(self):
        self.assertEqual(fit_column_widths([80, 150, 200], [40, 100, 180], 250), [40, 100, 180])

    def test_rounding_and_many_viewport_widths(self):
        low = [38, 90, 120, 110, 80, 192]
        for available in range(sum(low), 1800):
            result = fit_column_widths([60, 140, 300, 320, 120, 192], low, available, [0, 1, 1, 1, 0, 0])
            self.assertEqual(sum(result), available)
            self.assertTrue(all(value >= minimum for value, minimum in zip(result, low)))


if __name__ == "__main__":
    unittest.main()
