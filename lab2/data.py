import re
from typing import List

def find_dates_in_text(text: str) -> List[str]:
    """правильность дат"""
    pattern = r'\b(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.(1[0-9]{3}|2[0-9]{3})\b'
    matches = re.findall(pattern, text)
    return [f"{d}.{m}.{y}" for d, m, y in matches]

def is_valid_date_format(date_str: str) -> bool:
    """синтаксис"""
    pattern = r'^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.(1[0-9]{3}|2[0-9]{3})$'
    return bool(re.fullmatch(pattern, date_str))

def find_dates_in_file(filename: str) -> List[str]:
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return find_dates_in_text(f.read())
    except FileNotFoundError:
        return []


def is_leap_year(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def is_calendar_valid(date_str: str) -> bool:
    if not is_valid_date_format(date_str):
        return False

    day, month, year = map(int, date_str.split('.'))
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    if is_leap_year(year):
        days_in_month[1] = 29

    return day <= days_in_month[month - 1]

if __name__ == '__main__':
    dates = find_dates_in_file('input.txt')
    for d in dates:
        print(d)