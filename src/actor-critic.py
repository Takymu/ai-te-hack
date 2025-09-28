import ollama
import logging

from dataclasses import dataclass

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LLM_MODEL = 'llama3:8b' 

def get_word_data_with_local_llm():
    prompt = f"""
    привет
    """
    response = ollama.chat(
        model=LLM_MODEL,
        messages=[{'role': 'user', 'content': prompt}],
        format='json', # Указываем, что ждем JSON в ответе
        options={
            'num_predict': 200  # Максимальное количество токенов в ответе
        }
    )
    
    response_text = response['message']['content']
    return response_text


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
        """
        Инициализация системы генерации комиксов
        
        Args:
            model_actor: Модель-актер (генератор комиксов)
            model_critic: Модель-критик (оценщик качества)
            tokenizer: Токенизатор для обеих моделей
            config: Конфигурация генерации
        """
        self.config = config
        
        # Промпты для моделей
        self.actor_prompt_template = """Переделай исходный тест в стиле комикса. Измени стиль текста. Длина не больше исходного текста

            Исходный документ:
            {document}

            {feedback}

            Комикс:"""

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

            Улучши комикс, учитывая замечания критика:"""

    LLM_MODEL = 'llama3:8b' 


    def generate_text(self, prompt: str) -> str:
        response = ollama.chat(
            model=LLM_MODEL,
            messages=[{'role': 'user', 'content': prompt}],
        )
        
        return response['message']['content']


    def generate_comic(self, document: str) -> Dict:
        """
        Основной метод генерации комикса с итеративным улучшением
        
        Args:
            document: Исходный документ для преобразования
            
        Returns:
            Dict с результатами генерации
        """
        logger.info("Начинаем генерацию комикса...")
        
        # История итераций
        history = {
            "document": document,
            "iterations": [],
            "final_comic": "",
            "total_iterations": 0,
            "success": False
        }
        
        current_comic = ""
        
        for iteration in range(self.config.max_iterations):
            logger.info(f"Итерация {iteration + 1}/{self.config.max_iterations}")
            
            # Генерация комикса актером
            if iteration == 0:
                # Первая итерация - базовая генерация
                actor_prompt = self.actor_prompt_template.format(
                    document=document,
                    feedback=""
                )
            else:
                actor_prompt = self.actor_prompt_template.format(
                    document=current_comic,
                    feedback=f"\nОбратная связь от критика:\n{critic_response}\n"
                )
            
            current_comic = self.generate_text(
                actor_prompt
            )

            print(current_comic)
            
            # Проверка минимальной длины
            if len(current_comic) < self.config.min_comic_length:
                logger.warning(f"Комикс слишком короткий: {len(current_comic)} символов")
                current_comic += "\n[Комикс требует расширения...]"
            
            logger.info(f"Сгенерирован комикс длиной {len(current_comic)} символов")
            
            # Оценка критиком
            critic_prompt = self.critic_prompt_template.format(comic=current_comic)
            critic_response = self.generate_text(
                critic_prompt,
            )
            print(critic_response)
            
            # Парсинг ответа критика        
        return history


def main():
    """Основная функция для демонстрации работы системы"""    
    # Пример документа
    sample_document = """
    В исследовательской работе "Visualizing the Loss Landscape of Neural Nets" 
    авторы изучают структуру функций потерь нейронных сетей.
    """
    
    # Конфигурация
    config = GenerationConfig(
        max_iterations=5,
        actor_temperature=1.2,
        critic_temperature=0.3,
        min_comic_length=300
    )
    
    # Создание системы (здесь нужно подставить ваши модели)
    system = ComicGenerationSystem(config)
    
    # Генерация комикса
    results = system.generate_comic(sample_document)
    

if __name__ == "__main__":
    main()