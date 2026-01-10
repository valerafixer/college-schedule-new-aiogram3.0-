from aiogram.dispatcher.filters.state import State, StatesGroup

class ReplaceState(StatesGroup):
    text = State()
