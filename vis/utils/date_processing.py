
def generate_date_sequence(start_date, end_date, gap=1):
    DATE_INFO = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    buf = start_date.split('-')
    start_year, start_month, start_day = int(buf[0]), int(buf[1]), int(buf[2])
    buf = end_date.split('-')
    end_year, end_month, end_day = int(buf[0]), int(buf[1]), int(buf[2])
    
    current_year, current_month, current_day = start_year, start_month, start_day
    ret_arr = []

    while current_year < end_year or (current_year == end_year and current_month < end_month) or (current_year == end_year and current_month == end_month and current_day <= end_day):
        ret_year = str(current_year)
        ret_month = str(current_month) if current_month >= 10 else '0' + str(current_month)
        ret_day = str(current_day) if current_day >= 10 else '0' + str(current_day)
        current_day += gap
        if current_day > DATE_INFO[current_month - 1]:
            current_day -= DATE_INFO[current_month - 1]
            current_month = current_month + 1 if current_month != 12 else 1
            current_year = current_year if current_month != 1 else current_year + 1
        ret_arr.append(f'{ret_year}-{ret_month}-{ret_day}')
    return ret_arr


