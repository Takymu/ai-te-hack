# import ollama
from openai import OpenAI
from dataclasses import dataclass
from promptscenario import scenario_prompt
# LLM_MODEL = 'llama3:8b' 


@dataclass
class GenerationConfig:
    """Конфигурация для генерации"""
    max_iterations: int = 5
    max_length: int = 2048
    actor_temperature: float = 1.2  # Высокая температура для креативности
    critic_temperature: float = 0.3  # Низкая температура для точности
    min_comic_length: int = 0  # Минимальная длина комикса



class ComicGenerationSystem:
    def __init__(self, config: GenerationConfig):
        self.config = config

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="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",
        )
        
        self.actor_prompt_template = scenario_prompt

        self.critic_prompt_template = """Ты критик комиксов. Оцени качество следующего комикса по критериям:
                        1. Драматургия
                        2. Информативность
                        3. Общая читабельность
                        4. Визуальные сцены (должны быть наиболее простыми для удобства генерации)
                        5. Проверь что в сценах нет никакого текста кроме фраз персонажей (мы не можем рисовать текст на предметах!)
                        6. Проверь что во фразах персонажей нет никакого лишнего форматирования (фразы сразу пойдут в комикс напрямую)
                        Ни в коем случае не трогай теги в квадратных скобках, 
                        это ключевые слова для парсинга! Не делай по ним никаких замечаний.
                        
                        Комикс:
                        {comic}
                    """

        self.improvement_prompt = """
                        Предыдущий комикс:
                        {previous_comic}

                        Обратная связь критика:
                        {critic_feedback}

                        Переделай комикс, учитывая замечания критика:
                    """

    # LLM_MODEL = 'llama3:8b' 


    # def generate_text(self, prompt: str) -> str:
    #     response = ollama.chat(
    #         model=LLM_MODEL,
    #         messages=[{'role': 'user', 'content': prompt}],
    #     )
        
    #     return response['message']['content']


    def generate_text(self, promt):
        completion = self.client.chat.completions.create(
            extra_headers={},
            extra_body={},
            model="deepseek/deepseek-chat-v3.1:free",
            messages=[
                {
                    "role": "user",
                    "content":  promt
                }
            ]
        )
        return completion.choices[0].message.content


    def actor_critic_loop(self, document: str):        
        current_comic = ""
        critic_prompt = ""
        for iteration in range(self.config.max_iterations):
            
            if iteration == 0:
                actor_prompt = self.actor_prompt_template.format(document=document)
            else:
                actor_prompt = self.improvement_prompt.format(previous_comic=current_comic,
                    critic_feedback=critic_response)
            
            #* gen by actor
            current_comic = self.generate_text(actor_prompt)
            print("======ACTOR======")
            print(current_comic)
            print()
                        
            #* reword by critic
            if iteration != self.config.max_iterations - 1:
                critic_prompt = self.critic_prompt_template.format(comic=current_comic)
                critic_response = self.generate_text(critic_prompt)
                print("======CRITIC======")
                print(critic_response)
                print()

        return current_comic
            
    
def generate_comix_actcrit(document):
    config = GenerationConfig(
        max_iterations=2,
        actor_temperature=1.2,
        critic_temperature=0.3,
        min_comic_length=300
    )
    
    system = ComicGenerationSystem(config)
    
    return system.actor_critic_loop(document)

