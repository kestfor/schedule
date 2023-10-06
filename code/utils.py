import time
import datetime


def check_date_format(date: str) -> bool:
    try:
        valid_date = time.strptime(date, '%d.%m.%Y')
        curr_date = str(datetime.datetime.now().date()).split('-')
        curr_date.reverse()
        date = date.split('.')
        if curr_date[-1] > date[-1]:
            return False
        elif curr_date[-1] == date[-1] and curr_date[-2] > date[-2]:
            return False
        elif curr_date[-1] == date[-1] and curr_date[-2] == date[-2] and curr_date[0] > date[0]:
            return False
    except ValueError:
        return False
    else:
        return True


def check_time_format(time_to_check: str) -> bool:
    try:
        valid_time = time.strptime(time_to_check, '%H:%M')
    except ValueError:
        return False
    else:
        return True

