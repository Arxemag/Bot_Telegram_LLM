import logging
import os
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ContentType
from api_llm import get_llm_response

class VoiceStates(StatesGroup):
    waiting_for_voice = State()

class VoiceHandler:
    def __init__(self):
        self.router = Router()
        self.setup_handlers()

    def setup_handlers(self):
        self.router.message(Command(commands=['voice']))(self.start_voice)
        self.router.message(lambda message: message.content_type == ContentType.VOICE)(self.handle_voice_message)

    async def start_voice(self, message: types.Message, state: FSMContext):
        await state.set_state(VoiceStates.waiting_for_voice)
        await message.answer("Отправьте голосовое сообщение для обработки.")

    async def handle_voice_message(self, message: types.Message, state: FSMContext):
        try:
            audio = await message.voice.get_file()
            audio_path = f"voice_{message.from_user.id}.ogg"
            await audio.download(destination=audio_path)

            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data, language="ru-RU")

            llm_response = await get_llm_response(message.from_user.id, text, system_prompt="Вы — помощник для обработки голосовых сообщений.")
            logging.info(f"LLM Response: {llm_response}")
            await self.send_voice_message(message, llm_response)
        except sr.UnknownValueError:
            await message.answer("Извините, я не смог распознать речь.")
        except sr.RequestError as e:
            await message.answer(f"Ошибка сервиса распознавания речи: {e}")
        except Exception as e:
            logging.error(f"Произошла ошибка: {e}")
            await message.answer("Произошла ошибка при обработке вашего сообщения.")
        finally:
            if os.path.exists(audio_path):
                os.remove(audio_path)

    async def send_voice_message(self, message: types.Message, text: str):
        try:
            tts = gTTS(text=text, lang='ru')
            audio_file = BytesIO()
            tts.write_to_fp(audio_file)
            audio_file.seek(0)
            await message.answer_voice(audio_file, caption="Ответ от LLM")
        except Exception as e:
            logging.error(f"Ошибка при отправке голосового сообщения: {e}")
            await message.answer("Произошла ошибка при отправке голосового сообщения.")
        finally:
            audio_file.close()