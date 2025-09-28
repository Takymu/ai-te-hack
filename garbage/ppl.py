from transformers import pipeline
import torch

# Создание pipeline для генерации текста
pipe = pipeline(
    "text-generation",
    model="Qwen/Qwen2-7B-Instruct",
    torch_dtype=torch.float16,  # Используем float16 для экономии памяти
    device_map="auto"  # Автоматически распределяем на GPU/CPU
)

# Пример запроса
prompt = "Привет, расскажи мне шутку!"
response = pipe(
    prompt,
    max_length=100,  # Максимальная длина ответа
    num_return_sequences=1,  # Количество генерируемых последовательностей
    do_sample=True,  # Включаем случайную выборку
    top_k=50,  # Топ-k выборка
    top_p=0.95,  # Топ-p выборка
    temperature=0.7  # Температура для разнообразия ответов
)

# Вывод результата
print(response[0]["generated_text"])