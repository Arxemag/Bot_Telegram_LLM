import os

def get_prompt(personality: str) -> str:
    prompt_file = f"prompts/personality_prompts/{personality.lower()}.txt"
    if os.path.exists(prompt_file):
        with open(prompt_file, 'r', encoding='utf-8') as file:
            return file.read()
    return ""