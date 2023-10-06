from aiogram.types import CallbackQuery
from aiogram.dispatcher.router import Router
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardBuilder
from states import AddActivityState, GetActivityOffset
from data_base import db

router = Router()


@router.callback_query(F.data == "menu_callback")
async def menu_callback(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="добавить событие", callback_data="add_new_activity"))
    builder.row(InlineKeyboardButton(text="просмотреть события", callback_data="view_activities"))
    await callback.message.edit_text("выбери действие", reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "add_new_activity")
async def add_new_activity(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите желаемую дату в формате дд.мм.гггг")
    await state.set_state(AddActivityState.date)


async def handle_empty_list(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='меню', callback_data="menu_callback"))
    await callback.message.edit_text("здесь ничего нет", reply_markup=builder.as_markup())


def sort_filter(string: str):
    info = string.split()
    tmp = info[-1].split('.')
    tmp.reverse()
    tmp = '.'.join(tmp)
    info[-1] = tmp
    return tuple([info[-1], info[-2], info[-3]])


@router.callback_query(F.data == 'view_activities')
async def view_activities(callback: CallbackQuery, state: FSMContext):
    data = []
    user_id = callback.from_user.id
    if user_id not in db.users:
        await handle_empty_list(callback)
        return
    for item in db[user_id]:
        date = item["date"]
        time = item["time"]
        name = item["name"]
        data.append(name + '\n' + time + '\n' + date)
    data.sort(key=lambda x: sort_filter(x))
    await view_list(callback, state, data)


def get_offset(start, end, data):
    res = ""
    for i in range(start, end):
        res += f'{data[i]}' + '\n\n'
    return res


async def view_list(callback: CallbackQuery, state: FSMContext, data: list):
    users = data
    if not users:
        await handle_empty_list(callback)
    else:
        activities = data
        await state.set_state(GetActivityOffset.get_next)
        await state.update_data(start=0, end=min(10, len(activities)), events=activities)
        await get_next_data_offset(callback, state)


@router.callback_query(F.data == "get_next_data_offset")
async def get_next_data_offset(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    start = data["start"]
    end = data["end"]
    builder = InlineKeyboardBuilder()
    if start >= end:
        await handle_empty_list(callback)
        await state.clear()
        return
    activities = data["events"]
    text = get_offset(start, end, activities)
    builder.add(InlineKeyboardButton(text="далее", callback_data="get_next_data_offset"))
    builder.add(InlineKeyboardButton(text="в меню", callback_data="menu_callback"))
    await callback.message.edit_text(text=text, reply_markup=builder.as_markup())
    start += 10
    end = min(end + 10, len(activities))
    await state.update_data(start=start, end=end)
