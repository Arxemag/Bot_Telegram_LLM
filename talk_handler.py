import logging
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from api_llm import get_llm_response
from button import Keyboard

class TalkStates(StatesGroup):
    waiting_for_personality = State()
    chatting = State()

class TalkHandler:
    def __init__(self):
        self.router = Router()
        self.setup_handlers()

    def setup_handlers(self):
        self.router.message(Command(commands=['talk']))(self.start_talk)
        self.router.callback_query(lambda c: c.data.startswith('personality_'))(self.handle_personality_selection)
        self.router.message()(self.handle_message)

    async def start_talk(self, message: types.Message, state: FSMContext):
        await state.set_state(TalkStates.waiting_for_personality)
        await message.answer("Выберите известную личность для разговора:", reply_markup=await Keyboard.get_personality_buttons())

    async def handle_personality_selection(self, callback_query: types.CallbackQuery, state: FSMContext):
        personality = callback_query.data.split('_')[1]
        await state.update_data(personality=personality)
        await state.set_state(TalkStates.chatting)
        await callback_query.message.answer(f"Вы выбрали {personality}. Начните разговор, отправляя текстовые сообщения.")

    async def handle_message(self, message: types.Message, state: FSMContext):
        data = await state.get_data()
        personality = data.get('personality')
        if personality:
            prompt = f"Представьте, что вы {personality}. Ответьте на следующее сообщение: {message.text}"
            llm_response = await get_llm_response(message.from_user.id, prompt, system_prompt="Вы — помощник для имитации разговора с известной личностью.")
            logging.info(f"LLM Response: {llm_response}")
            await message.answer(llm_response)
        else:
            await message.answer("Пожалуйста, сначала выберите известную личность.")