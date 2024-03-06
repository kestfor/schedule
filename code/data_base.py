from datetime import datetime

import apscheduler.schedulers.asyncio
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from apscheduler.job import Job
from config_reader import config
import os
import utils
import json


class LocalDataBase:
    __instance = None
    __notification_time = (8, 0)

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        self._DATA_PATH = config.data_path.get_secret_value()
        self._data = self._load_data()
        self._jobs = {}
        self._scheduler: apscheduler.schedulers.asyncio.AsyncIOScheduler = None
        self._bot = None

    def add_bot(self, bot):
        self._bot = bot

    def add_scheduler(self, scheduler):
        self._scheduler = scheduler
        self._load_scheduler()

    def __load_dict(self, file_name) -> dict:
        if os.path.exists(f"{self._DATA_PATH}/{file_name}") and os.path.getsize(f"{self._DATA_PATH}/{file_name}") > 0:
            with open(f"{self._DATA_PATH}/{file_name}", "r", encoding="utf-8") as file:
                res = json.load(file)
                return res
        return {}

    def __update_file(self, data, file_name) -> None:
        with open(f"{self._DATA_PATH}/{file_name}", "w", encoding="utf-8") as file:
            if data is not None and len(data) > 0:
                file.write(json.dumps(data, ensure_ascii=False, indent=4))

    def _add_event_to_scheduler(self, full_date, text, chat_id):
        full_date = full_date.copy()
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text='меню', callback_data="menu_callback"))
        job_set: Job = self._scheduler.add_job(self._bot.send_message, "date",
                                               args=[chat_id, text],
                                               kwargs={"reply_markup": builder.as_markup()},
                                               run_date=datetime(*full_date))
        full_date[-1] = 59
        full_date[-2] = 23
        job_clear: Job = self._scheduler.add_job(self._clear_day, "date",
                                                 args=[chat_id, self.from_full_date(full_date)],
                                                 run_date=datetime(*full_date))
        if chat_id not in self._jobs:
            self._jobs[chat_id] = {}
        self._jobs[chat_id][self.from_full_date(full_date)] = {"notification": job_set.id, "cleaner": job_clear.id}

    def _load_scheduler(self):
        for chat_id in self._data:
            for date in self[chat_id]:
                text = self.__get_text(self[chat_id][date])
                full_date = self.__to_full_date(date, self.__notification_time)
                self._add_event_to_scheduler(full_date, text, chat_id)

    def _load_data(self) -> dict:
        tmp = self.__load_dict("users_events.json")
        res = {}
        for key, value in tmp.items():
            res[int(key)] = value
        return res

    def _clear_day(self, chat_id: int, date: str):
        if chat_id not in self._data:
            return
        if date not in self[chat_id]:
            return
        self[chat_id].pop(date)
        try:
            job_clear = self._jobs[chat_id][date]["cleaner"]
            job_set = self._jobs[chat_id][date]["notification"]
            self._scheduler.remove_job(job_id=job_set)
            self._scheduler.remove_job(job_id=job_clear)
        except Exception as err:
            print(err)

    def remove_event(self, chat_id: int, date: str, name):
        if chat_id not in self._data:
            return
        if date not in self[chat_id]:
            return
        for curr_name in self[chat_id][date]:
            if curr_name == name:
                self[chat_id][date].pop(name)
                if len(self[chat_id][date]) == 0:
                    try:
                        job_clear = self._jobs[chat_id][date]["cleaner"]
                        job_set = self._jobs[chat_id][date]["notification"]
                        self._scheduler.remove_job(job_id=job_set)
                        self._scheduler.remove_job(job_id=job_clear)
                    except Exception as err:
                        print(err)
                    self[chat_id].pop(date)
                else:
                    tmp = {}
                    for key in self[chat_id][date]:
                        tmp[key] = self[chat_id][date][key][1] - self[chat_id][date][key][0]
                    self[chat_id][date] = utils.get_schedule(tmp)
                    self.update_events(chat_id, date, self[chat_id][date])
                self._update_data()
                break

    def _update_data(self) -> None:
        self.__update_file(self._data, "users_events.json")

    @property
    def users(self):
        return [key for key in self._data]

    def __getitem__(self, item):
        return self._data[item]

    @staticmethod
    def __to_full_date(date: str, time_duration) -> list:
        date = date.split('.')
        date.reverse()
        date = [int(i) for i in date]
        time = [time_duration[0], 0]
        full_date = date + time
        return full_date

    @staticmethod
    def from_full_date(date: list) -> str:
        tmp = date.copy()
        tmp.reverse()
        tmp = tmp[2:]
        return '.'.join([str(i) for i in tmp])

    def add_new_user(self, chat_id: int):
        if chat_id not in self._data:
            self._data[chat_id] = {}
            self._update_data()

    @staticmethod
    def __get_text(activities: dict):
        text = list()
        for name, duration in activities.items():
            text.append([name, tuple(duration)])
        text.sort(key=lambda x: x[-1])
        text = [f"{item[0]} с {item[1][0]} до {item[1][1]}" for item in text]
        return '\n'.join(text)

    def get_activities(self, chat_id: int, date: str):
        res = self[chat_id][date].copy()
        return res

    def get_formatted_activities(self, chat_id: int, date: str) -> str:
        activities = self.__get_text(self[chat_id][date])
        return activities

    def update_events(self, chat_id, date: str, activities: dict):
        if chat_id not in self._data:
            self.add_new_user(chat_id)
        text = self.__get_text(activities)
        text = "Распорядок дня на сегодня\n" + text
        if date not in self._data[chat_id]:
            self._data[chat_id][date] = {}
        else:
            try:
                job_clear = self._jobs[chat_id][date]["cleaner"]
                job_set = self._jobs[chat_id][date]["notification"]
                self._scheduler.remove_job(job_id=job_set)
                self._scheduler.remove_job(job_id=job_clear)
            except Exception as err:
                print(err)

        for name in activities:
            self._data[chat_id][date][name] = activities[name]

        self._add_event_to_scheduler(self.__to_full_date(date, self.__notification_time), text, chat_id)
        self._update_data()


db = LocalDataBase()
