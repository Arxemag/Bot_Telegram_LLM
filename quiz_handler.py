import logging
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from api_llm import get_llm_response
from button import Keyboard
from quiz import Quiz
import json

class QuizHandler:
    def __init__(self):
        self.quiz = Quiz()
        self.router = Router()
        self.setup_handlers()

    def setup_handlers(self):
        # Обработчик команды /quiz
        self.router.message(Command(commands=['quiz']))(self.start_quiz)
        # Обработчик выбора темы
        self.router.callback_query(lambda c: c.data.startswith('theme_'))(self.handle_theme_selection)
        # Обработчик выбора ответа
        self.router.callback_query(lambda c: c.data.startswith('answer_'))(self.handle_answer_selection)
        # Обработчик опций викторины
        self.router.callback_query(lambda c: c.data.startswith('quiz_'))(self.handle_quiz_options)

    async def start_quiz(self, message: types.Message, state: FSMContext):
        await state.set_state(self.quiz.QuizStates.waiting_for_theme)
        await message.answer("Выберите тему для викторины:", reply_markup=await Keyboard.get_theme_buttons())

    async def handle_theme_selection(self, callback_query: types.CallbackQuery, state: FSMContext):
        theme = callback_query.data.split('_')[1]
        await callback_query.message.answer(self.quiz.set_theme(theme))
        question_prompt = (
            f"Создай вопрос для викторины на тему {theme} с вариантами ответов A, B, C, D. "
            f"Ответ должен быть на русском языке. Формат ответа: "
            f'{{"question": "вопрос", "options": ["A) вариант 1", "B) вариант 2", "C) вариант 3", "D) вариант 4"], "answer": "правильный ответ"}}'
        )
        llm_response = await get_llm_response(callback_query.from_user.id, question_prompt, self.quiz.system_prompt)
        logging.info(f"LLM Response for question: {llm_response}")

        try:
            llm_response_json = json.loads(llm_response)
            await self.quiz.get_question(llm_response)  # Сохраняем вопрос и ответ в объекте quiz
            await callback_query.message.answer(
                f"<b>{llm_response_json['question']}</b>",
                reply_markup=await Keyboard.get_answer_buttons(llm_response_json["options"]),
                parse_mode="HTML"
            )
            await state.set_state(self.quiz.QuizStates.waiting_for_answer)
        except json.JSONDecodeError as e:
            logging.error(f"JSONDecodeError: {e}")
            await callback_query.message.answer("Произошла ошибка при обработке ответа от LLM. Пожалуйста, попробуйте еще раз.", reply_markup=await Keyboard.get_main_menu(), parse_mode="HTML")

    async def handle_answer_selection(self, callback_query: types.CallbackQuery, state: FSMContext):
        answer = callback_query.data.split('_')[1]
        result = self.quiz.check_answer(answer)
        await callback_query.message.answer(result, reply_markup=await Keyboard.get_quiz_options(), parse_mode="HTML")
        await state.set_state(self.quiz.QuizStates.waiting_for_theme)

    async def handle_quiz_options(self, callback_query: types.CallbackQuery, state: FSMContext):
        action = callback_query.data.split('_')[1]
        if action == "next":
            question_prompt = (
                f"Создай вопрос для викторины на тему {self.quiz.current_theme} с вариантами ответов A, B, C, D. "
                f"Ответ должен быть на русском языке. Формат ответа: "
                f'{{"question": "вопрос", "options": ["A) вариант 1", "B) вариант 2", "C) вариант 3", "D) вариант 4"], "answer": "правильный ответ"}}'
            )
            llm_response = await get_llm_response(callback_query.from_user.id, question_prompt, self.quiz.system_prompt)
            logging.info(f"LLM Response for next question: {llm_response}")

            try:
                llm_response_json = json.loads(llm_response)
                await self.quiz.get_question(llm_response)  # Сохраняем вопрос и ответ в объекте quiz
                await callback_query.message.answer(
                    f"<b>{llm_response_json['question']}</b>",
                    reply_markup=await Keyboard.get_answer_buttons(llm_response_json["options"]),
                    parse_mode="HTML"
                )
                await state.set_state(self.quiz.QuizStates.waiting_for_answer)
            except json.JSONDecodeError as e:
                logging.error(f"JSONDecodeError: {e}")
                await callback_query.message.answer("Произошла ошибка при обработке ответа от LLM. Пожалуйста, попробуйте еще раз.", reply_markup=await Keyboard.get_main_menu(), parse_mode="HTML")
        elif action == "change_theme":
            await callback_query.message.answer("Выберите новую тему для викторины:", reply_markup=await Keyboard.get_theme_buttons())
            await state.set_state(self.quiz.QuizStates.waiting_for_theme)
        elif action == "end":
            self.quiz.end_quiz()
            await callback_query.message.answer(f"Викторина закончена. Ваш итоговый счет: {self.quiz.score}", reply_markup=await Keyboard.get_main_menu(), parse_mode="HTML")
            await state.finish()
