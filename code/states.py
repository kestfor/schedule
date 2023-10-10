from aiogram.fsm.state import State, StatesGroup


class AddActivityState(StatesGroup):
    activity = State()

class ViewActivityState(StatesGroup):
    view = State()

class GetActivityOffset(StatesGroup):
    get_next = State()
