from aiogram.dispatcher.router import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardButton
from states import AddActivityState, ViewActivityState
from aiogram.fsm.context import FSMContext
from data_base import db
from custom_datetime import DateTime
from aiogram import F
from utils import ActivitiesParser, alg


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


@router.message(AddActivityState.activity, F.text)
async def add_new_activity(message: Message, state: FSMContext):
    chat_id = message.from_user.id
    activities = message.text
    try:
        new_activities: dict = ActivitiesParser.parse(activities)
    except SyntaxError:
        await message.answer("неверный формат")
        return
    data = await state.get_data()
    date = data["day"]
    date_str = str(date)
    if chat_id not in db.users:
        db.add_new_user(chat_id)
    old_activities = {}
    if date_str in db[chat_id]:
        old_activities = db.get_activities(chat_id, date_str)
        for activity, duration in old_activities.items():
            old_activities[activity] = duration[-1] - duration[0]
    full_day = old_activities | new_activities
    # TODO алгоритмическая функция
    try:
        res = alg(full_day)
    except OverflowError:
        await state.clear()
        builder = InlineKeyboardBuilder()
        builder.button(text="выбрать другой день", callback_data="pick_another_day")
        await message.answer("не хватает времени, выберите другой день", reply_markup=builder.as_markup())
    else:
        builder = InlineKeyboardBuilder()
        builder.button(text="в меню", callback_data="menu_callback")
        db.update_events(chat_id, date_str, full_day)
        await message.answer("распорядок дня успешно изменен", reply_markup=builder.as_markup())
