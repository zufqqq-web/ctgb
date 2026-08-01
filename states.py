from aiogram.fsm.state import State, StatesGroup

class AddGenre(StatesGroup):
    waiting_name = State()

class AddMovie(StatesGroup):
    choosing_genre = State()
    waiting_title = State()
    waiting_description = State()
    waiting_year = State()
    waiting_file = State()

class DeleteMovie(StatesGroup):
    waiting_choice = State()

class DeleteGenre(StatesGroup):
    waiting_choice = State()