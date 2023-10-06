from datetime import datetime

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config_reader import config
import os
import json
from events import Event


class LocalDataBase:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        self._DATA_PATH = config.data_path.get_secret_value()
        self._data = self._load_data()
        self._scheduler = None
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

    def _add_event_to_scheduler(self, full_date, name, chat_id):
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text='меню', callback_data="menu_callback"))
        self._scheduler.add_job(self._bot.send_message, "date", args=[chat_id, name],
                                kwargs={"reply_markup": builder.as_markup()},
                                run_date=datetime(*full_date))
        self._scheduler.add_job(self.remove_event, "date", args=[chat_id, name],
                                run_date=datetime(*full_date))

    def _load_scheduler(self):
        for chat_id in self._data:
            for event in self._data[chat_id]:
                full_date = self.__convert_date(event)
                name = event["name"]
                self._add_event_to_scheduler(full_date, name, chat_id)

    def _load_data(self) -> dict:
        tmp = self.__load_dict("users_events.json")
        res = {}
        for key, value in tmp.items():
            res[int(key)] = value
        return res

    def remove_event(self, chat_id: int, name: str):
        if chat_id not in self._data:
            return
        for event in self[chat_id]:
            if event["name"] == name:
                self[chat_id].remove(event)
                self._update_data()

    def _update_data(self) -> None:
        self.__update_file(self._data, "users_events.json")

    @property
    def users(self):
        return [key for key in self._data]

    def __getitem__(self, item):
        return self._data[item]

    @staticmethod
    def __convert_date(event: dict):
        date: list = event["date"].split('.')
        date.reverse()
        date = [int(item) for item in date]
        time = event["time"].split(':')
        time = [int(item) for item in time]
        full_date = date + time
        return full_date

    def add_new_user(self, chat_id: int):
        if chat_id not in self._data:
            self._data[chat_id] = []
            self._update_data()

    def add_new_event(self, chat_id, event: Event):
        in_dict = event.to_dict()
        self._data[chat_id].append(in_dict)
        self._update_data()
        name = in_dict["name"]
        full_date = self.__convert_date(in_dict)
        self._add_event_to_scheduler(full_date, name, chat_id)


db = LocalDataBase()
