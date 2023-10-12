from aiogram.types import CallbackQuery
from aiogram.dispatcher.router import Router
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardBuilder
from states import AddActivityState, GetActivityOffset, ViewActivityState
from data_base import db
from aiogram.filters.callback_data import CallbackData
from custom_datetime import DateTime
import datetime

router = Router()


class DaysCallbackFactory(CallbackData, prefix="fabday"):
    action: str
    value: datetime.date


class ActivitiesCallbackFactory(CallbackData, prefix="fabact"):
    action: str
    date: str
    name: str


def get_week_keyboard(action: str, start: int = None, full_weak: bool = True, dash: bool = False):
    builder = InlineKeyboardBuilder()
    week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    week_rus = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
    today = datetime.date.today()
    if start is None:
        start = today.isoweekday() - 1
    if full_weak:
        if dash:
            start += 1
            today = today + datetime.timedelta(1)
        for i in range(start, len(week) + start):
            builder.button(text=week_rus[i % 7], callback_data=DaysCallbackFactory(action=action, value=today))
            today = today + datetime.timedelta(1)
        builder.button(text="в меню", callback_data="menu_callback")
        builder.adjust(1)
        return builder.as_markup()
    else:
        builder.button(text=week_rus[start], callback_data=DaysCallbackFactory(action=action, value=today))
        builder.button(text="в меню", callback_data="menu_callback")
        builder.adjust(1)
        return builder.as_markup()


@router.callback_query(F.data == "menu_callback")
async def menu_callback(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="добавить событие", callback_data="add_new_activity"))
    builder.row(InlineKeyboardButton(text="просмотреть события", callback_data="view_activities"))
    await callback.message.edit_text("выбери действие", reply_markup=builder.as_markup())
    await callback.answer()


async def handle_empty_list(callback: CallbackQuery, **kwargs):
    builder = InlineKeyboardBuilder()
    for key in kwargs:
        builder.row(InlineKeyboardButton(text=key, callback_data=kwargs[key]))
    builder.row(InlineKeyboardButton(text='меню', callback_data="menu_callback"))
    await callback.message.edit_text("здесь ничего нет", reply_markup=builder.as_markup())
    await callback.answer()


def sort_filter(string: str):
    info = string.split()
    tmp = info[-1].split('.')
    tmp.reverse()
    tmp = '.'.join(tmp)
    info[-1] = tmp
    return tuple([info[-1], info[-2], info[-3]])


@router.callback_query(F.data == 'view_activities')
async def view_activities_fab(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("выберите день недели", reply_markup=get_week_keyboard("view", dash=False))


@router.callback_query(F.data == "add_new_activity")
async def add_new_activity_fab(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("выберите день недели", reply_markup=get_week_keyboard("add"))


@router.callback_query(DaysCallbackFactory.filter())
async def callback_view_days(callback: CallbackQuery, state: FSMContext, callback_data: DaysCallbackFactory):
    if callback_data.action == "view":
        await state.set_state(ViewActivityState.view)
        day = DateTime(callback_data.value)
        await state.update_data(day=day)
        await view_activities(callback, state)
    elif callback_data.action == "add":
        await state.set_state(AddActivityState.activity)
        day = DateTime(callback_data.value)
        await state.update_data(day=day)
        text = ('Введите событие(я) в формате:\n'
                '"название1" - "кол-во часов"\n'
                '"название2" - "кол-во часов"')
        await callback.message.edit_text(text)


# def get_offset(start, end, data):
#     res = ""
#     for i in range(start, end):
#         res += f'{data[i]}' + '\n\n'
#     return res
#
#
# async def view_list(callback: CallbackQuery, state: FSMContext, data: list):
#     users = data
#     if not users:
#         await handle_empty_list(callback)
#     else:
#         activities = data
#         await state.set_state(GetActivityOffset.get_next)
#         await state.update_data(start=0, end=min(10, len(activities)), events=activities)
#         await get_next_data_offset(callback, state)
#
#
# @router.callback_query(F.data == "get_next_data_offset")
# async def get_next_data_offset(callback: CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     start = data["start"]
#     end = data["end"]
#     builder = InlineKeyboardBuilder()
#     if start >= end:
#         await handle_empty_list(callback)
#         await state.clear()
#         return
#     activities = data["events"]
#     text = get_offset(start, end, activities)
#     builder.add(InlineKeyboardButton(text="далее", callback_data="get_next_data_offset"))
#     builder.add(InlineKeyboardButton(text="в меню", callback_data="menu_callback"))
#     await callback.message.edit_text(text=text, reply_markup=builder.as_markup())
#     start += 10
#     end = min(end + 10, len(activities))
#     await state.update_data(start=start, end=end)


@router.callback_query(F.data == 'pick_another_day')
async def pick_another_day(callback: CallbackQuery):
    await callback.message.edit_text("Выберите день", reply_markup=get_week_keyboard("add"))


@router.callback_query(F.data == 'check_another_day')
async def pick_another_day(callback: CallbackQuery):
    await callback.message.edit_text("Выберите день", reply_markup=get_week_keyboard("view", dash=False))


async def view_activities(callback: CallbackQuery, state: FSMContext):
    chat_id = callback.from_user.id
    data = await state.get_data()
    date = data["day"]
    date_str = str(date)
    if chat_id not in db.users:
        db.add_new_user(chat_id)
    if date_str not in db[chat_id] or len(db.get_activities(chat_id, date_str)) == 0:
        await handle_empty_list(callback, назад="check_another_day")
        return
    else:
        activities = db.get_formatted_activities(chat_id, date_str)
        builder = InlineKeyboardBuilder()
        builder.button(text='удалить занятие', callback_data="remove_activity")
        builder.button(text="назад", callback_data="check_another_day")
        builder.button(text="в меню", callback_data="menu_callback")
        builder.adjust(1)
        await callback.message.edit_text(text=activities, reply_markup=builder.as_markup())


@router.callback_query(F.data == "remove_activity")
async def remove_activity(callback: CallbackQuery, state: FSMContext):
    chat_id = callback.from_user.id
    data = await state.get_data()
    date = data["day"]
    date_str = str(date)
    activities_dict = db.get_activities(chat_id, date_str)
    builder = InlineKeyboardBuilder()
    for activity in activities_dict:
        builder.button(text=activity, callback_data=ActivitiesCallbackFactory(action="remove",
                                                                              name=activity,
                                                                              date=date_str))
    builder.button(text='назад', callback_data="check_another_day")
    builder.button(text="в меню", callback_data="menu_callback")
    builder.adjust(1)
    await callback.message.edit_text("выберите активность", reply_markup=builder.as_markup())


@router.callback_query(ActivitiesCallbackFactory.filter())
async def handle_activity_callback_factory(callback: CallbackQuery, callback_data: ActivitiesCallbackFactory):
    if callback_data.action == "remove":
        db.remove_event(callback.from_user.id, callback_data.date, callback_data.name)
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="назад", callback_data="check_another_day"))
        builder.row(InlineKeyboardButton(text="в меню", callback_data="menu_callback"))
        await callback.message.edit_text(text=f'"{callback_data.name}" удалено из списка',
                                         reply_markup=builder.as_markup())
    else:
        await handle_empty_list(callback)
