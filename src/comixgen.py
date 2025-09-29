from openai import OpenAI
import os
from .promptscenario import scenario_prompt

def generate_comix(doctext):
    try:
        load_dotenv(find_dotenv())
    except Exception:
        pass

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY не найден в окружении/.env")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "http://localhost",
            "X-Title": "ai-te-hack-telegram-bot",
        },
        extra_body={},
        model="deepseek/deepseek-chat-v3.1:free",
        messages=[
            {
                "role": "user",
                "content": scenario_prompt.format(document=doctext)
            }
        ]
    )
    return completion.choices[0].message.content