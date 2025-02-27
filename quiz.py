import json
import logging
from aiogram.fsm.state import State, StatesGroup

class QuizStates(StatesGroup):
    waiting_for_theme = State()
    waiting_for_answer = State()

class Quiz:
    def __init__(self):
        self.current_question = None
        self.current_options = None
        self.correct_answer = None
        self.score = 0
        self.current_theme = None
        self.system_prompt = (
            "Вы — помощник для создания вопросов викторины. "
            "Создавайте вопросы с четырьмя вариантами ответов (A, B, C, D) на заданную тему. "
            "Ответ должен быть в формате JSON: "
            '{"question": "вопрос", "options": ["A) вариант 1", "B) вариант 2", "C) вариант 3", "D) вариант 4"], "answer": "правильный ответ"}.'
        )

    async def get_question(self, llm_response):
        """
        Сохраняет вопрос, варианты ответа и правильный ответ из ответа LLM.
        """
        try:
            data = json.loads(llm_response)
            self.current_question = data['question']
            self.current_options = data['options']
            self.correct_answer = data['answer']  # Сохраняем правильный ответ
            logging.info(f"Question saved: {self.current_question}")
            logging.info(f"Correct answer: {self.correct_answer}")
        except json.JSONDecodeError as e:
            logging.error(f"JSONDecodeError in get_question: {e}")
            raise ValueError("Не удалось обработать ответ от LLM.")

    def check_answer(self, user_answer, correct_answer_text):
        """
        Проверяет ответ пользователя и возвращает результат.
        """
        logging.info(f"Checking answer: {user_answer} against {correct_answer_text}")
        if user_answer == correct_answer_text:
            self.score += 1
            return "Правильно! 🎉"
        else:
            return f"Неправильно. Правильный ответ: {correct_answer_text}"

    def set_theme(self, theme):
        """
        Устанавливает тему викторины.
        """
        self.current_theme = theme
        return f"Тема викторины установлена: {theme}"

    def end_quiz(self):
        """
        Завершает викторину и сбрасывает состояние.
        """
        final_score = self.score
        self.score = 0
        self.current_theme = None
        self.current_question = None
        self.current_options = None
        self.correct_answer = None
        return final_score