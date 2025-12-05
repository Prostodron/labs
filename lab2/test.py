import unittest
from data import (
    is_valid_date_format,
    find_dates_in_text,
    find_dates_in_file,
    is_calendar_valid,
    is_leap_year
)

class TestDateUtils(unittest.TestCase):

    def test_valid_dates_syntax(self):
        self.assertTrue(is_valid_date_format("01.01.2020"))
        self.assertTrue(is_valid_date_format("31.12.2999"))
        self.assertTrue(is_valid_date_format("29.02.2024"))

    def test_invalid_dates_syntax(self):
        self.assertFalse(is_valid_date_format("1.1.2020"))
        self.assertFalse(is_valid_date_format("01-01-2020"))
        self.assertFalse(is_valid_date_format("32.13.2024"))
        self.assertFalse(is_valid_date_format("00.00.0000"))
        self.assertFalse(is_valid_date_format("01.01.999"))
        self.assertFalse(is_valid_date_format("01.01.3000"))

    def test_find_dates_in_text(self):
        text = "Даты: 05.06.2021 и 17.08.2022. Ошибки: 32.13.2023."
        result = find_dates_in_text(text)
        self.assertEqual(result, ["05.06.2021", "17.08.2022"])

    def test_find_dates_in_file(self):
        dates = find_dates_in_file("input.txt")
        self.assertIn("01.01.2020", dates)
        self.assertIn("31.12.2049", dates)

    def test_file_not_found(self):
        self.assertEqual(find_dates_in_file("missing.txt"), [])

    def test_leap_year(self):
        self.assertTrue(is_leap_year(2024))
        self.assertTrue(is_leap_year(2000))
        self.assertFalse(is_leap_year(1900))
        self.assertFalse(is_leap_year(2023))

    def test_calendar_validity(self):
        self.assertTrue(is_calendar_valid("29.02.2024"))
        self.assertFalse(is_calendar_valid("29.02.2023"))
        self.assertTrue(is_calendar_valid("29.02.2000"))
        self.assertFalse(is_calendar_valid("29.02.1900"))
        self.assertTrue(is_calendar_valid("31.01.2024"))
        self.assertFalse(is_calendar_valid("31.04.2024"))
        self.assertFalse(is_calendar_valid("1.1.2024"))
        self.assertFalse(is_calendar_valid("abc"))

    def test_empty_input(self):
        self.assertFalse(is_valid_date_format(""))
        self.assertEqual(find_dates_in_text(""), [])
if __name__ == '__main__':
    unittest.main()