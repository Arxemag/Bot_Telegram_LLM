from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery, FSInputFile
from api_llm import get_llm_response, clear_context
from button import Keyboard
from quiz_handler import QuizHandler
from random_fact_handler import RandomFactHandler
from programmer_handler import ProgrammerHandler
import json
import logging

router = Router()
quiz_handler = QuizHandler()
random_fact_handler = RandomFactHandler()
programmer_handler = ProgrammerHandler()

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
    programmer_handler.exit_programmer_mode()
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
    await quiz_handler.handle_theme_selection(callback_query)

# Обработчик выбора ответа
@router.callback_query(lambda c: c.data.startswith('answer_'))
async def handle_answer_selection(callback_query: CallbackQuery):
    await quiz_handler.handle_answer_selection(callback_query)

# Обработчик опций викторины
@router.callback_query(lambda c: c.data.startswith('quiz_'))
async def handle_quiz_options(callback_query: CallbackQuery):
    await quiz_handler.handle_quiz_options(callback_query)

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

# Обработчик команды /programmer
@router.message(Command(commands=['programmer']))
async def handle_programmer_command(message: types.Message):
    await programmer_handler.send_programmer_help(message)

# Обработчик текстовых сообщений
@router.message()
async def handle_message(message: types.Message):
    user_message = message.text
    if quiz_handler.quiz.in_quiz_mode:
        check_prompt = f"Проверь ответ на вопрос: {quiz_handler.quiz.current_question}. Ответ пользователя: {user_message}."
        llm_response = await get_llm_response(message.from_user.id, check_prompt, quiz_handler.system_prompt)
        logging.info(f"LLM Response for check: {llm_response}")

        try:
            llm_response_json = json.loads(llm_response)
            result = quiz_handler.quiz.check_answer(user_message, llm_response_json)
            await message.answer(result, reply_markup=await Keyboard.get_quiz_options(), parse_mode="HTML")
        except json.JSONDecodeError as e:
            logging.error(f"JSONDecodeError: {e}")
            await message.answer("Произошла ошибка при обработке ответа от LLM. Пожалуйста, попробуйте еще раз.", reply_markup=await Keyboard.get_main_menu(), parse_mode="HTML")
    elif programmer_handler.in_programmer_mode:
        await programmer_handler.handle_programmer_message(message)
    else:
        await message.answer("Выберите команду.", reply_markup=await Keyboard.get_main_menu(), parse_mode="HTML")
