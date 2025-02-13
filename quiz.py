import random
import logging
import json

class Quiz:
    def __init__(self):
        self.themes = ["Программирование", "История", "Наука", "Искусство", "Спорт"]
        self.current_theme = None
        self.current_question = None
        self.current_answer = None
        self.score = 0
        self.in_quiz_mode = False
        self.options = []

    def start_quiz(self):
        self.in_quiz_mode = True
        self.score = 0
        return "Выберите тему для викторины:", self.themes

    def set_theme(self, theme):
        self.current_theme = theme
        return f"Вы выбрали тему: {theme}. Получаю вопрос..."

    async def get_question(self, llm_response):
        try:
            llm_response_json = json.loads(llm_response)
            self.current_question = llm_response_json["question"]
            self.current_answer = llm_response_json["answer"]
            self.options = llm_response_json["options"]
            logging.info(f"Current question: {self.current_question}")
            logging.info(f"Current answer: {self.current_answer}")
            logging.info(f"Options: {self.options}")
            return self.current_question
        except json.JSONDecodeError as e:
            logging.error(f"JSONDecodeError: {e}")
            return "Произошла ошибка при обработке ответа от LLM. Пожалуйста, попробуйте еще раз."

    def check_answer(self, user_answer):
        logging.info(f"User answer: {user_answer}")
        # Убираем пробелы и сравниваем ответ пользователя с правильным ответом
        if user_answer.strip() == self.current_answer.strip():
            self.score += 1
            return f"Правильно! Ваш счет: {self.score}"
        else:
            return f"Неправильно! Правильный ответ: {self.current_answer}. Ваш счет: {self.score}"

    def end_quiz(self):
        self.in_quiz_mode = False
        self.current_theme = None
        self.current_question = None
        self.current_answer = None
        self.score = 0
        self.options = []
