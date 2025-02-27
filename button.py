from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

class Keyboard:
    @staticmethod
    async def get_main_menu():
        buttons = [
            [KeyboardButton(text="/start")],
            [KeyboardButton(text="/help")],
            [KeyboardButton(text="/clear")],
            [KeyboardButton(text="/quiz")],
            [KeyboardButton(text="/random")],
            [KeyboardButton(text="/programmer")],
            [KeyboardButton(text="/talk")]
        ]
        keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
        return keyboard

    @staticmethod
    async def get_theme_buttons():
        themes = ["Программирование", "История", "Наука", "Искусство", "Спорт"]
        buttons = [InlineKeyboardButton(text=theme, callback_data=f"theme_{theme}") for theme in themes]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
        return keyboard

    @staticmethod
    async def get_quiz_options():
        buttons = [
            [InlineKeyboardButton(text="Еще вопрос", callback_data="quiz_next")],
            [InlineKeyboardButton(text="Сменить тему", callback_data="quiz_change_theme")],
            [InlineKeyboardButton(text="Закончить викторину", callback_data="quiz_end")]
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        return keyboard

    @staticmethod
    async def get_answer_buttons(options):
        buttons = [InlineKeyboardButton(text=option, callback_data=f"answer_{option.split(') ')[1]}") for option in options]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[btn] for btn in buttons])  # Размещаем каждую кнопку на отдельной строке
        return keyboard

    @staticmethod
    async def get_random_fact_buttons():
        buttons = [
            [InlineKeyboardButton(text="Хочу ещё факт", callback_data="random_next")],
            [InlineKeyboardButton(text="Закончить", callback_data="random_end")]
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        return keyboard

    @staticmethod
    async def get_personality_buttons():
        # Маппинг: {"Отображаемое имя": "имя_файла"}
        personalities = {
            "Альберт Эйнштейн": "einstein",
            "Леонардо да Винчи": "da_vinci",
            "Илон Маск": "musk",
            "Стив Джобс": "jobs",
        }

        buttons = [
            InlineKeyboardButton(
                text=display_name,
                callback_data=f"personality_{file_name}"
            )
            for display_name, file_name in personalities.items()
        ]

        keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
        return keyboard