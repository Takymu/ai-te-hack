from openai import OpenAI

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
      "content": "What is the meaning of life?"
    }
  ]
)
print(completion.choices[0].message.content)