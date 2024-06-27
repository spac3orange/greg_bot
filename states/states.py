from aiogram.fsm.state import StatesGroup, State


class CreateForm(StatesGroup):
    input_name = State()
    input_age = State()
    input_photo = State()
    input_photo2 = State()
    input_photo3 = State()
    input_photo4 = State()
    input_games = State()
    input_description = State()
    input_price = State()


class ReqMoney(StatesGroup):
    input_card = State()


class Admmailing(StatesGroup):
    input_message = State()


class SetStatusOnline(StatesGroup):
    input_hours = State()
