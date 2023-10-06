from aiogram.fsm.state import State, StatesGroup


class AddActivityState(StatesGroup):
    date = State()
    time = State()
    activity = State()


class GetActivityOffset(StatesGroup):
    get_next = State()
