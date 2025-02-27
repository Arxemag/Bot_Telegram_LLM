import os


def get_prompt(personality: str) -> str:
    file_path = os.path.join("prompts", f"{personality}.txt")
    print(f"[DEBUG] Reading prompt from: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read().strip()
            print(f"[DEBUG] Prompt content: {content}")
            return content
    except FileNotFoundError:
        print(f"[ERROR] File {file_path} not found!")
        return None

# Тестовый вызов функции
if __name__ == "__main__":
    test_personality = "musk"  # Пример: проверка для Илона Маска
    result = get_prompt(test_personality)
    print(f"Результат: {result}")