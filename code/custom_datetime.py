import datetime
from typing import Optional


class DateTime:
    _week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    _week_rus = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]

    def __init__(self, date: datetime.date):
        self._year = date.year
        self._month = date.month
        self._day = date.day
        self._day_ind = date.isoweekday()
        self._date = date

    @property
    def date(self):
        return self._date

    def day_of_the_week(self):
        return self._week[self._day_ind - 1]

    def __add__(self, other: int):
        new_date = self._date + datetime.timedelta(other)
        return DateTime(new_date)

    def __iadd__(self, other: int):
        self.__init__(self._date + datetime.timedelta(other))
        return self

    def __str__(self):
        return f'{self._day}.{self._month}.{self._year}'

    def __repr__(self):
        return self.__str__()

    def __radd__(self, other: int):
        return self.__add__(other)
