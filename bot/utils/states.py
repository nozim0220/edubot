"""All FSM states in one place for easy management."""
from aiogram.fsm.state import State, StatesGroup


class MainMenuState(StatesGroup):
    idle = State()


class ProfileEditState(StatesGroup):
    waiting_age = State()
    waiting_region = State()
    waiting_school = State()
    waiting_dream_uni = State()
    waiting_target_score = State()
    waiting_phone = State()


class QuizState(StatesGroup):
    in_quiz = State()
    reviewing = State()


class AIState(StatesGroup):
    selecting_type = State()
    chatting = State()


class UniversitySearchState(StatesGroup):
    waiting_query = State()
    waiting_budget = State()
    browsing = State()


class ReminderSetupState(StatesGroup):
    waiting_time = State()


class BroadcastState(StatesGroup):
    waiting_message = State()
    waiting_audience = State()
    confirming = State()
