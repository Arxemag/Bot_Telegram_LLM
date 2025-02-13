import logging
from aiogram.types import FSInputFile, CallbackQuery
from api_llm import get_llm_response
from button import Keyboard

class RandomFactHandler:
    def __init__(self):
        self.system_prompt = """
        Ты — помощник для предоставления интересных фактов. Твоя задача — генерировать интересные факты на русском языке.
        """

    async def send_random_fact(self, message):
        photo = FSInputFile(r'F:\PythonCod\Bot_Telegram_LLM\image\random.jpg')  # Используем FSInputFile
        await message.answer_photo(photo=photo, caption="Вот ваш рандомный факт!")

        # Запрос к ChatGPT с заранее заготовленным промптом
        random_fact_prompt = "Расскажи интересный факт на русском языке."
        llm_response = await get_llm_response(message.from_user.id, random_fact_prompt, self.system_prompt)

        # Отправляем ответ пользователю
        await message.answer(llm_response, reply_markup=await Keyboard.get_random_fact_buttons(), parse_mode="HTML")

    async def handle_random_end(self, callback_query: CallbackQuery):
        await callback_query.message.answer("Возврат в главное меню.", reply_markup=await Keyboard.get_main_menu(), parse_mode="HTML")

    async def handle_random_next(self, callback_query: CallbackQuery):
        # Запрос к ChatGPT с заранее заготовленным промптом
        random_fact_prompt = "Расскажи интересный факт на русском языке."
        llm_response = await get_llm_response(callback_query.from_user.id, random_fact_prompt, self.system_prompt)

        # Отправляем ответ пользователю
        await callback_query.message.answer(llm_response, reply_markup=await Keyboard.get_random_fact_buttons(), parse_mode="HTML")
