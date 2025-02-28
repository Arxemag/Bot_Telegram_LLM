import logging
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from api_llm import get_llm_response, clear_context
from button import Keyboard
from quiz_handler import QuizHandler
from random_fact_handler import RandomFactHandler
from talk_handler import TalkHandler
from voice_handler import VoiceHandler
import json

router = Router()
quiz_handler = QuizHandler()
random_fact_handler = RandomFactHandler()
talk_handler = TalkHandler()
voice_handler = VoiceHandler()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

# Обработчик команды /start
@router.message(Command(commands=['start']))
async def send_welcome(message: types.Message):
    quiz_handler.quiz.end_quiz()
    await message.answer("Привет! Я ваш Telegram бот. Выберите команду:",
                         reply_markup=await Keyboard.get_main_menu(), parse_mode="HTML")

# Обработчик команды /help
@router.message(Command(commands=['help']))
async def send_help(message: types.Message):
    await message.answer("Помощь: Вы можете отправлять мне текстовые сообщения, и я отвечу с помощью LLM.",
                         reply_markup=await Keyboard.get_main_menu(), parse_mode="HTML")

# Обработчик команды /clear
@router.message(Command(commands=['clear']))
async def clear_user_context(message: types.Message):
    await clear_context(message.from_user.id)
    await message.answer("Контекст очищен.", reply_markup=await Keyboard.get_main_menu(), parse_mode="HTML")

# Обработчик команды /quiz
@router.message(Command(commands=['quiz']))
async def start_quiz(message: types.Message):
    photo = FSInputFile(r'F:\PythonCod\Bot_Telegram_LLM\image\quiz.jpg')  # Используем FSInputFile
    await message.answer_photo(photo=photo, caption="Добро пожаловать в викторину!")
    await message.answer("Выберите тему для викторины:", reply_markup=await Keyboard.get_theme_buttons())

# Обработчик выбора темы
@router.callback_query(lambda c: c.data.startswith('theme_'))
async def handle_theme_selection(callback_query: CallbackQuery):
    state = FSMContext(storage=MemoryStorage(), key=callback_query.from_user.id)
    await quiz_handler.handle_theme_selection(callback_query, state=state)

# Обработчик выбора ответа
@router.callback_query(lambda c: c.data.startswith('answer_'))
async def handle_answer_selection(callback_query: CallbackQuery):
    state = FSMContext(storage=MemoryStorage(), key=callback_query.from_user.id)
    await quiz_handler.handle_answer_selection(callback_query, state=state)

# Обработчик опций викторины
@router.callback_query(lambda c: c.data.startswith('quiz_'))
async def handle_quiz_options(callback_query: CallbackQuery):
    state = FSMContext(storage=MemoryStorage(), key=callback_query.from_user.id)
    await quiz_handler.handle_quiz_options(callback_query, state=state)

# Обработчик команды /random
@router.message(Command(commands=['random']))
async def handle_random_command(message: types.Message):
    await random_fact_handler.send_random_fact(message)

# Обработчик нажатия на кнопку "Закончить"
@router.callback_query(lambda c: c.data == 'random_end')
async def handle_random_end_callback(callback_query: CallbackQuery):
    await random_fact_handler.handle_random_end(callback_query)

# Обработчик нажатия на кнопку "Хочу ещё факт"
@router.callback_query(lambda c: c.data == 'random_next')
async def handle_random_next_callback(callback_query: CallbackQuery):
    await random_fact_handler.handle_random_next(callback_query)

# Обработчик команды /talk
@router.message(Command(commands=['talk']))
async def handle_talk_command(message: types.Message, state: FSMContext):
    await talk_handler.start_talk(message, state=state)

# Обработчик выбора личности
@router.callback_query(lambda c: c.data.startswith('personality_'))
async def handle_personality_selection(callback_query: CallbackQuery):
    state = FSMContext(storage=MemoryStorage(), key=callback_query.from_user.id)
    await talk_handler.handle_personality_selection(callback_query, state=state)

# Обработчик сообщений в режиме разговора
@router.message()
async def handle_talk_message(message: types.Message, state: FSMContext):
    await talk_handler.handle_message(message, state=state)

# Обработчик команды /voice
@router.message(Command(commands=['voice']))
async def handle_voice_command(message: types.Message, state: FSMContext):
    await voice_handler.start_voice(message, state=state)

# Обработчик голосовых сообщений
@router.message(lambda message: message.content_type == ContentType.VOICE)
async def handle_voice_message(message: types.Message, state: FSMContext):
    await voice_handler.handle_voice_message(message, state=state)