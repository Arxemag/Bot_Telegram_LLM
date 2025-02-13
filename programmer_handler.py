import logging
from aiogram.types import FSInputFile, CallbackQuery
from api_llm import get_llm_response
from button import Keyboard

class ProgrammerHandler:
    def __init__(self):
        self.system_prompt = """
        Ты — помощник для программистов. Твоя задача — помогать с кодом, отвечать на вопросы по программированию, анализировать логи и помогать находить ошибки.
        """
        self.in_programmer_mode = False

    async def send_programmer_help(self, message):
        photo = FSInputFile(r'F:\PythonCod\Bot_Telegram_LLM\image\programmer.jpg')  # Используем FSInputFile
        await message.answer_photo(photo=photo, caption="Вот ваш помощник по программированию!")

        # Запрос к ChatGPT с заранее заготовленным промптом
        programmer_prompt = "Я помощник по программированию. Как я могу помочь?"
        llm_response = await get_llm_response(message.from_user.id, programmer_prompt, self.system_prompt)

        # Включаем режим программиста
        self.in_programmer_mode = True

        # Отправляем ответ пользователю
        await message.answer(llm_response, reply_markup=await Keyboard.get_main_menu(), parse_mode="HTML")

    async def handle_programmer_message(self, message):
        if self.in_programmer_mode:
            # Запрос к ChatGPT с текущим сообщением пользователя
            llm_response = await get_llm_response(message.from_user.id, message.text, self.system_prompt)
            await message.answer(llm_response, reply_markup=await Keyboard.get_main_menu(), parse_mode="HTML")
        else:
            await message.answer("Выберите команду.", reply_markup=await Keyboard.get_main_menu(), parse_mode="HTML")

    async def exit_programmer_mode(self):
        self.in_programmer_mode = False
