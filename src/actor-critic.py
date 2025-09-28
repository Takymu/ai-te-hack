# import ollama
from openai import OpenAI
from dataclasses import dataclass

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
        
        self.actor_prompt_template = """Привет. Я сейчас дам тебе документ. Задание следующее: необходимо придумать по нему комикс. Будь креативен. Напиши сценарий комикса. Читатель комикса должен будет в нескучном формате, в виде истории с сюжетом, завязкой, развитием действия, кульминацией, и развязкой узнать основную информацию из документа. Для каждой сцены приведи следующие поля:
                        Описание сцены - начинается с [scene], заканчивается на [endscene], содержит небольшое по объему описание сцены, ракурса и действий персонажей для генеративной модели. Максимум два персонажа в сцене, один слева другой справа. Никаких надписей на предметах сцены писать нельзя.
                        фразы персонажей - сначала левый, если есть, начинается с [charL], заканчивается на [charLend], затем правый, если есть, начинается с [charR], заканчивается на [charRend] - то, что говорит каждый из персонажей.
                        Комикс не должен быть слишком большим, но должен отражать основные положения документа в виде интересной истории. При этом описания должны быть короткими.
                        Также в самом начале приведи краткое, но емкое описание персонажей комикса, чтобы генеративная нейросеть смогла их нарисовать, помни, это промпт будет.
                        описание первого персонажа (который всегда слева) начинается с [charLdescStart], заканчивается на [charLdecEnd] описание второго (который всегда справа)
                        начинается на [charRdescStart] и заканчивается на [charRdescEnd]. Очень аккуратно все эти плашечки выставляй, это важно.
                        Если персонаж ничего не говорит, напиши [placeholder] вместо его фразы. Никаких пояснений в скобках во фразах персонажей, эти фразы сразу пойдут в облака текста.    
                        Приведу пример описания сцены. Начало примера:

                        [scene]
                        здесь находится текст описания сцены и действий персонажей, без их слов
                        [endscene]
                        [charL]
                        Фраза первого персонажа ИЛИ [placeholder] если персонаж молчит
                        [charLend]
                        [charR]
                        Фраза второго персонажа ИЛИ [placeholder] если персонаж молчит
                        [charRend]

                        всё, конец примера. Дальше напишешь сразу начало описания следующей сцены.
                        если хочешь, можешь написать план сюжета комикса перед началом описания персонажей и сцен, чисто для себя. 
                        Описания персонажей и сцен должны быть на английском, при этом фразы персонажей должны быть на русском, будь внимателен.
                        В описаниях персонажей должна быть только их внешность, такая, какая будет сохранена на протяжении всего комикса
                        Итак, вот текст документа:\n\n {document}
                    """

        self.critic_prompt_template = """Ты критик комиксов. Оцени качество следующего комикса по критериям:
                        1. Интересность сюжета
                        3. Описание визуальных сцен
                        4. Общая читабельность

                        Комикс:
                        {comic}
                    """

        self.improvement_prompt = """
                        Предыдущий комикс:
                        {previous_comic}

                        Обратная связь критика:
                        {critic_feedback}

                        Улучши комикс, учитывая замечания критика:
                    """

    LLM_MODEL = 'llama3:8b' 


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
        
        for iteration in range(self.config.max_iterations):
            
            if iteration == 0:
                actor_prompt = self.actor_prompt_template.format(document=document)
            else:
                actor_prompt = self.improvement_prompt.format(previous_comic=current_comic,
                    critic_feedback=critic_response)
            
            #* gen by actor
            current_comic = self.generate_text(actor_prompt)
            print(f"======ACTOR======")
            print(current_comic)
            print()
                        
            #* reword by critic
            critic_prompt = self.critic_prompt_template.format(comic=current_comic)
            critic_response = self.generate_text(critic_prompt)
            print("======CRITIC======")
            print(critic_response)
            print()

        return current_comic
            


def main():
    sample_document = """
    В исследовательской работе "Visualizing the Loss Landscape of Neural Nets" 
    авторы изучают структуру функций потерь нейронных сетей.
    """
    
    config = GenerationConfig(
        max_iterations=5,
        actor_temperature=1.2,
        critic_temperature=0.3,
        min_comic_length=300
    )
    
    system = ComicGenerationSystem(config)
    
    results = system.actor_critic_loop(sample_document)

    print("====RESULT=====")
    print(results)
    

if __name__ == "__main__":
    main()