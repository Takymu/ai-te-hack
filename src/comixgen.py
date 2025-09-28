from openai import OpenAI

from promptscenario import scenario_prompt

def generate_comix(doctext):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="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",
    )

    completion = client.chat.completions.create(
        extra_headers={},
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