from aiogram.dispatcher.router import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardButton
from states import AddActivityState
from aiogram import F
from aiogram.fsm.context import FSMContext
import utils
from events import Event
from data_base import db


router = Router()


@router.message(Command("start"))
async def start_handler(message: Message):
    text = "давай составим твое расписание"
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="начать", callback_data="menu_callback"))
    await message.answer(text, reply_markup=builder.as_markup())


@router.message(Command("menu"))
async def menu_handler(message: Message):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="добавить событие", callback_data="add_new_activity"))
    builder.row(InlineKeyboardButton(text="просмотреть события", callback_data="view_activities"))
    await message.answer("выбери действие", reply_markup=builder.as_markup())


@router.message(AddActivityState.date, F.text)
async def get_date_of_new_activity(message: Message, state: FSMContext):
    date = message.text
    if not utils.check_date_format(date):
        await message.answer("Некорректная дата или формат даты\nВведите желаемую дату в формате дд.мм.гггг")
        return
    await state.update_data(date=date)
    await message.answer("Введите время в 24 формате в виде чч:мм")
    await state.set_state(AddActivityState.time)


@router.message(AddActivityState.time, F.text)
async def get_time_of_new_activity(message: Message, state: FSMContext):
    time = message.text
    data = await state.get_data()
    date = data["date"]
    if not utils.check_time_format(time):
        await message.answer("Некорректное время или формат времени\nВведите время в 24 формате в виде чч:мм")
        return
    for event in db[message.from_user.id]:
        if event["date"] == date and event["time"] == time:
            await message.answer("Это время уже занято")
            return
    await state.update_data(time=time)
    await message.answer("Введите название события")
    await state.set_state(AddActivityState.activity)


@router.message(AddActivityState.activity, F.text)
async def get_name_of_new_activity(message: Message, state: FSMContext):
    name = message.text
    data = await state.get_data()
    new_event = Event(data["date"], data["time"], name)
    if message.from_user.id not in db.users:
        db.add_new_user(message.from_user.id)
    db.add_new_event(message.from_user.id, new_event)
    await state.clear()
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="меню", callback_data="menu_callback"))
    await message.answer("Новое событие успешно добавлено", reply_markup=builder.as_markup())
