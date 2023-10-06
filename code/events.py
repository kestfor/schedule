import datetime


class Event:

    def __init__(self, date: datetime.date, time: datetime.time, name: str):
        self._date = date
        self._time = time
        self._name = name

    @property
    def date(self):
        return self._date

    @property
    def time(self):
        return self._time

    @property
    def name(self):
        return self._name

    def to_dict(self) -> dict:
        return {"name": self._name, "date": self._date, "time": self._time}

    def __str__(self):
        return str(self._name) + '\n' + str(self._time) + '\n' + str(self._date)

