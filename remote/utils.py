import re
from functools import cmp_to_key

def _comp(a : str, b: str) -> int:
    date_pattern = re.compile(r"(\d{4})(\d{2})(\d{2})")
    a_date, b_date = date_pattern.search(a), date_pattern.search(b)
    if (not a) and b:
        return -1
    if (a and (not b)) or ((not a) and (not b)):
        return 1
    a_year, a_month, a_day = int(a_date.group(1)), int(a_date.group(2)), int(a_date.group(3))
    b_year, b_month, b_day = int(b_date.group(1)), int(b_date.group(2)), int(b_date.group(3))
    if a_year != b_year:
        return 1 if a_year > b_year else -1
    if a_month != b_month:
        return 1 if a_month > b_month else -1
    if a_day != b_day:
        return 1 if a_day > b_day else -1
    return 0

def sort_measure_cycle(cycles : list[str]) -> None:
    cycles.sort(key=cmp_to_key(_comp))