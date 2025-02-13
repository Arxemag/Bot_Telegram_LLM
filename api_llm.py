import os
import logging
from mistralai import Mistral
from dotenv import load_dotenv
import json

# Загрузка переменных окружения из файла api.env
load_dotenv('api.env')

# Получение API-ключа из переменной окружения
api_key = os.getenv("MISTRAL_API_KEY")
model = "mistral-small"

# Инициализация клиента Mistral
client = Mistral(api_key=api_key)

# Словарь для хранения контекста пользователей
user_contexts = {}

async def get_llm_response(user_id, user_message, system_prompt):
    if user_id not in user_contexts:
        user_contexts[user_id] = []

    # Добавляем системное сообщение только один раз
    if not user_contexts[user_id]:
        system_message = {"role": "system", "content": system_prompt}
        user_contexts[user_id].append(system_message)

    # Логируем текущее сообщение пользователя
    logging.info(f"User message: {user_message}")

    # Добавляем текущее сообщение пользователя в контекст
    user_contexts[user_id].append({"role": "user", "content": user_message})

    # Логируем контекст перед отправкой запроса
    logging.info(f"Context before request: {user_contexts[user_id]}")

    chat_response = client.chat.complete(
        model=model,
        messages=user_contexts[user_id]
    )

    # Логируем ответ от LLM
    llm_response = chat_response.choices[0].message.content
    logging.info(f"LLM Response: {llm_response}")

    # Добавляем ответ LLM в контекст
    user_contexts[user_id].append({"role": "assistant", "content": llm_response})

    return llm_response

async def clear_context(user_id):
    if user_id in user_contexts:
        del user_contexts[user_id]
