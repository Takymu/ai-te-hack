from __future__ import annotations
import os
import tempfile
from typing import Optional

from .pdftotext import extract_text_from_pdf
from .scenparser import parse_scenario
from .diffusion import generate_image
from .yolo_detect import detect_faces
from .addovals import add_speech_bubble
from .imgcombine import combine_images_to_file
from .actor_critic import generate_comix_actcrit


def generate_comic_from_pdf(pdf_path: str, output_path: Optional[str] = None) -> str:
    """
    Полный конвейер: PDF -> текст -> сценарий -> изображения сцен -> пузырьки речи -> финальная картинка.

    Args:
        pdf_path: путь к входному PDF
        output_path: путь для сохранения результата (PNG). Если None, создаётся во временной папке.

    Returns:
        Путь к итоговому файлу PNG.
    """
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"Файл не найден: {pdf_path}")

    # Извлечение текста
    doctext = extract_text_from_pdf(pdf_path)

    # Генерация сценария (актор-критик) с фолбэком на локальный пример при ошибке авторизации/сети
    try:
        scenario_text = generate_comix_actcrit(doctext)
    except Exception as e:
        print(f"[pipeline] Не удалось сгенерировать сценарий через LLM: {e}")
        # Фолбэк на локальный пример
        fallback_path = os.path.join(os.path.dirname(__file__), 'scenariopamatka.txt')
        if os.path.isfile(fallback_path):
            with open(fallback_path, 'r', encoding='utf-8') as f:
                scenario_text = f.read()
            print("[pipeline] Использую локальный сценарий из scenariopamatka.txt")
        else:
            raise

    # Парсинг сценария на сцены и реплики
    scenario = parse_scenario(scenario_text)
    # Валидация: если сцен нет (LLM вернул мета-текст/критика), используем локальный фолбэк
    if not scenario.get('scenes'):
        print("[pipeline] Сцен после парсинга нет. Перехожу на локальный сценариопамятку.")
        fallback_path = os.path.join(os.path.dirname(__file__), 'scenariopamatka.txt')
        if os.path.isfile(fallback_path):
            with open(fallback_path, 'r', encoding='utf-8') as f:
                scenario_text = f.read()
            scenario = parse_scenario(scenario_text)
        else:
            raise RuntimeError("Сценарий пуст и отсутствует локальный фолбэк scenariopamatka.txt")

    charLdesc = scenario['charLdesc'][0] if scenario['charLdesc'] else None
    charRdesc = scenario['charRdesc'][0] if scenario['charRdesc'] else None

    scenelist: list[bytes] = []

    def _sanitize_dialogue(s: Optional[str]) -> Optional[str]:
        if s is None:
            return None
        # remove simple markdown emphasis to avoid **bold** etc.
        for token in ("**", "*", "__", "_"):
            s = s.replace(token, "")
        return s.strip()

    for i in range(len(scenario['scenes'])):
        scenedesc = scenario['scenes'][i]
        charLaction = scenario['charLaction'][i] if i < len(scenario['charLaction']) else None
        charRaction = scenario['charRaction'][i] if i < len(scenario['charRaction']) else None
        charLaction = _sanitize_dialogue(charLaction)
        charRaction = _sanitize_dialogue(charRaction)

        sceneprompt = f"""
{scenedesc}
It's a part of comic book with characters in the comix style, draw full-length characters.
The characters should be cartoony, 2D, suitable for a comic, and not overly complex and not overly expressive.
"""
        if charLaction is not None and charLdesc:
            sceneprompt += 'Appearance of left character:\n' + charLdesc + '\n'
        
        if charRaction is not None and charRdesc:
            sceneprompt += 'Appearance of right character:\n' + charRdesc + '\n'

        sceneprompt += 'location is absent of people'

        # Генерация изображения сцены с перехватом ошибок (фиксированный размер для стабильной вёрстки)
        try:
            img_bytes, _ext = generate_image(sceneprompt, width=832, height=512)
        except Exception as e:
            print(f"[pipeline] Не удалось сгенерировать сцену {i+1}: {e}")
            continue

        # Детекция лиц и добавление "облачков" с репликами
        faces = detect_faces(img_bytes)
        left = True

        # Сортировка лиц слева-направо, если два лица
        if len(faces) == 2 and faces[0][0] > faces[1][0]:
            face = faces[0]
            faces[0] = faces[1]
            faces[1] = face

        for x, y in faces:
            if left and charLaction is not None:
                img_bytes = add_speech_bubble(
                    img_bytes,
                    charLaction,
                    x,
                    y,
                    max_bubble_width=280,
                    min_font_size=8,
                )
                left = False
            elif charRaction is not None:
                img_bytes = add_speech_bubble(
                    img_bytes,
                    charRaction,
                    x,
                    y,
                    max_bubble_width=280,
                    min_font_size=8,
                )
        scenelist.append(img_bytes)

    # Куда сохраняем результат
    if output_path is None:
        tmpdir = tempfile.mkdtemp(prefix="comix_")
        output_path = os.path.join(tmpdir, "comic.png")

    if not scenelist:
        raise RuntimeError("Не удалось сгенерировать ни одной сцены комикса. Попробуйте ещё раз или другой документ.")

    combine_images_to_file(scenelist, output_path)
    return output_path
