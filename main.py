import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from router import router
from api_llm import clear_context
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из файла api.env
load_dotenv('api.env')

# Получение токенов из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Регистрация маршрутизатора
dp.include_router(router)

# Команды бота
commands = [
    BotCommand(command="/start", description="Начать"),
    BotCommand(command="/help", description="Помощь"),
    BotCommand(command="/clear", description="Очистить контекст"),
    BotCommand(command="/quiz", description="Начать викторину"),
    BotCommand(command="/random", description="Получить случайный факт"),
    BotCommand(command="/programmer", description="Начать режим программиста"),
    BotCommand(command="/talk", description="Начать разговор с известной личностью")
]

# Запуск бота
async def main():
    await bot.set_my_commands(commands)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())