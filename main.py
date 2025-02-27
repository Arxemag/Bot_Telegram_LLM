import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile
from dotenv import load_dotenv
import os
import asyncio
from router import router
from button import Keyboard


# Загрузка переменных окружения из файла api.env
load_dotenv('api.env')

# Получение токена из переменной окружения
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

# Инициализация бота и хранилища
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Middleware для обработки ошибок
class ErrorHandlingMiddleware:
    async def __call__(self, handler, event, data):
        try:
            return await handler(event, data)
        except Exception as e:
            logging.error(f"Ошибка: {e}")
            try:
                await event.message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.", reply_markup=await Keyboard.get_main_menu(), parse_mode="HTML")
            except Exception as e:
                logging.error(f"Ошибка при отправке сообщения об ошибке: {e}")

async def main():
    # Добавление middleware для обработки ошибок
    dp.message.middleware(ErrorHandlingMiddleware())
    # Добавление роутеров
    dp.include_router(router)
    # Запуск поллинга
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
