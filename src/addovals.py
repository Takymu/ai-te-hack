import argparse
import os
import sys
import math
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, List, Optional
import textwrap




def add_speech_bubbles_multiple(
    image: Image.Image,
    bubbles: list[dict],
    MAX_BUBBLE_WIDTH: int = 200,
    MIN_FONT_SIZE: int = 6,
    BORDER_COLOR = "black",
    FILL_COLOR = "white",
    TEXT_COLOR = "black",
    BORDER_WIDTH: int = 3,
    UP_HEAD: int = 80,
    RATIO_HEAD: float = 0.6,
    RATIO_ELLIPSE: float = 0.6
) -> Image.Image:
    """
    MAX_BUBBLE_WIDTH - макс. ширина эллипса
    MIN_FONT_SIZE - минимальный размер шрифта, для читаемости
    BORDER_COLOR - цвет рамки "облачков"
    FILL_COLOR - цвет заливки облачков
    TEXT_COLOR - цвет самого текста
    BORDER_WIDTH - размер рамки
    UP_HEAD - насколько поднимать над головой (переданной точкой точкой) [Можно рассчитывать на основе размера головы]
    RATIO_HEAD - где располагать точку треугольнику между центром жллипса и переданной точкой 
            (0 - в центре, 0.5 - между, 1.0 - оставить угол треугольника на голове)
    RATIO_ELLIPSE - опустить точки треугольника с фокуса эллипса ближе к низу эллипса (0 на фокусе, 1 на низе)


    bubbles:

    Список облаков передаётся как список словарей. Каждый словарь описывает одно облако и должен содержать следующие ключи:
    - "text" : str
        Текст, который будет отображён в облаке.
    - "head_coords" : Tuple[int, int]
        Координаты головы персонажа (x, y), к которой будет «тянуться» хвостик треугольника.
    - "font_path" : Optional[str]
        Путь к файлу шрифта (если None — используется шрифт по умолчанию).
    - "MAX_BUBBLE_WIDTH" : Optional[int]
        Максимальная ширина облака для переноса текста (по умолчанию 200).
    - "MIN_FONT_SIZE" : Optional[int]
        Минимальный размер шрифта при вычислении под размер текста (по умолчанию 6).

    После создания облаков их позиции могут быть скорректированы функцией, которая предотвращает наложение эллипсов друг на друга. 
    Коррекция учитывает:
    1. Размер текста + внутренний padding (BUBBLE_PADDING) для эллипса.
    2. Толщину рамки (BORDER_WIDTH), которая добавляется к каждой стороне.
    3. Расстановку эллипсов по обеим осям (x и y) для красивого распределения, если облака пересекаются.

    Пример словаря для одного облака:
    bubbles = [
        {
            "text": "Привет!",
            "head_coords": (100, 500),
            "font_path": "comic.ttf",
            "MAX_BUBBLE_WIDTH": 200,
            "MIN_FONT_SIZE": 8
        },
        {
            "text": "Как дела?",
            "head_coords": (700, 500)
            # font_path, MAX_BUBBLE_WIDTH, MIN_FONT_SIZE можно опустить для использования дефолтов
        }
    ]
    """


    result_image = image.copy()
    draw = ImageDraw.Draw(result_image)

    # ------------------- Подготовка облаков -------------------
    prepared_bubbles = []

    for b in bubbles:
        # head_coords = (int(b["head_x"]), int(b["head_y"]))
        head_coords = b["head_coords"]
        text = b["text"]

        # Font
        base_font_size = 40
        scale = 1 / math.sqrt(len(text) / 20 + 1)
        font_size = max(int(base_font_size * scale), MIN_FONT_SIZE)
        font = ImageFont.truetype(b.get("font_path") or "arial.ttf", font_size)

        # Wrap text
        max_chars = max(1, int(MAX_BUBBLE_WIDTH / (font_size * 0.6)))
        wrapped_lines = textwrap.wrap(text, width=max_chars)
        wrapped_text = "\n".join(wrapped_lines)

        # Text size
        text_bbox = draw.multiline_textbbox((0,0), wrapped_text, font=font, spacing=4)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]

        # Ellipse size
        padding = 15
        ellipse_w = text_w + 2*padding + 2*BORDER_WIDTH
        ellipse_h = text_h + 2*padding + 2*BORDER_WIDTH

        # Initial coordinates
        cx, cy = head_coords
        x1 = cx - ellipse_w//2
        y1 = cy - ellipse_h - UP_HEAD  # поднять над головой
        x2 = x1 + ellipse_w
        y2 = y1 + ellipse_h

        prepared_bubbles.append({
            "head_coords": head_coords,
            "wrapped_text": wrapped_text,
            "font": font,
            "rect": [x1, y1, x2, y2],
            "ellipse_w": ellipse_w,
            "ellipse_h": ellipse_h
        })

    # ------------------- Коррекция позиций -------------------
    def rects_overlap(r1, r2):
        x11, y11, x12, y12 = r1
        x21, y21, x22, y22 = r2
        return not (x12 < x21 or x22 < x11 or y12 < y21 or y22 < y11)

    max_iter = 100
    for _ in range(max_iter):
        moved = False
        for i in range(len(prepared_bubbles)):
            for j in range(i+1, len(prepared_bubbles)):
                r1 = prepared_bubbles[i]["rect"]
                r2 = prepared_bubbles[j]["rect"]
                if rects_overlap(r1, r2):
                    # Сдвиг по обеим осям
                    dx = (r1[2]-r1[0])//2
                    dy = (r1[3]-r1[1])//2
                    prepared_bubbles[i]["rect"][0] -= dx//2
                    prepared_bubbles[i]["rect"][2] -= dx//2
                    prepared_bubbles[i]["rect"][1] -= dy//2
                    prepared_bubbles[i]["rect"][3] -= dy//2

                    prepared_bubbles[j]["rect"][0] += dx//2
                    prepared_bubbles[j]["rect"][2] += dx//2
                    prepared_bubbles[j]["rect"][1] += dy//2
                    prepared_bubbles[j]["rect"][3] += dy//2

                    moved = True
        if not moved:
            break

    # ------------------- Рисуем облака -------------------
    def get_ellipse_foci(x1, y1, x2, y2):
        cx = (x1 + x2)//2
        cy = (y1 + y2)//2
        a = abs(x2 - x1)/2
        b = abs(y2 - y1)/2
        if a>=b:
            c = math.sqrt(a*a - b*b)
            return (int(cx-c), cy), (int(cx+c), cy), (cx, cy)
        else:
            c = math.sqrt(b*b - a*a)
            return (cx, int(cy-c)), (cx, int(cy+c)), (cx, cy)

    def interpolate_point(center, head, RATIO_HEAD=RATIO_HEAD):
        cx, cy = center
        hx, hy = head
        return (int(cx + (hx-cx)*RATIO_HEAD), int(cy + (hy-cy)*RATIO_HEAD))

    def scale_polygon(points, scale):
        cx = sum(p[0] for p in points)/len(points)
        cy = sum(p[1] for p in points)/len(points)
        return [(int(cx + (x-cx)*scale), int(cy + (y-cy)*scale)) for x,y in points]

    def draw_bubble(draw, b):
        x1,y1,x2,y2 = b["rect"]
        f1,f2,center = get_ellipse_foci(x1,y1,x2,y2)

        # если эллипс слишком большой (или вообще всегда?..), стоит приспустить верх треугольника от фокусов ближе ко дну эллипса
        how_much_down = (y2 - y1) // 2 # расстояние от фокуса до низа

        tmp_x, tmp_y = f1
        f1 = tmp_x, tmp_y + how_much_down*RATIO_ELLIPSE
        tmp_x, tmp_y = f2
        f2 = tmp_x, tmp_y + how_much_down*RATIO_ELLIPSE



        tip = interpolate_point(center, b["head_coords"], RATIO_HEAD=RATIO_HEAD)
        triangle = [f1,f2,tip]

        scale_factor = 1 + BORDER_WIDTH/20
        triangle_border = scale_polygon(triangle, scale_factor)

        # Border
        draw.ellipse([x1-BORDER_WIDTH,y1-BORDER_WIDTH,x2+BORDER_WIDTH,y2+BORDER_WIDTH], fill=BORDER_COLOR)
        draw.polygon(triangle_border, fill=BORDER_COLOR)

        # Bubble
        draw.ellipse([x1,y1,x2,y2], fill=FILL_COLOR)
        draw.polygon(triangle, fill=FILL_COLOR)

        # Text
        text_bbox = draw.multiline_textbbox((0,0), b["wrapped_text"], font=b["font"], spacing=4)
        text_w = text_bbox[2]-text_bbox[0]
        text_h = text_bbox[3]-text_bbox[1]

        cx = (x1+x2)//2
        cy = (y1+y2)//2
        draw.multiline_text((cx - text_w//2, cy - text_h//2), b["wrapped_text"], font=b["font"], fill=TEXT_COLOR, align="center", spacing=4)

    for b in prepared_bubbles:
        draw_bubble(draw, b)

    return result_image










def parse_coords(coord_str: str) -> Tuple[int, int]:
    """
    Парсит строку с координатами в формате 'x,y' или '(x,y)'
    """
    coord_str = coord_str.strip('() ')
    parts = coord_str.split(',')
    
    if len(parts) != 2:
        raise ValueError(f"Неправильный формат координат: {coord_str}. Ожидается 'x,y' или '(x,y)'")
    
    try:
        x = int(parts[0].strip())
        y = int(parts[1].strip())
        return (x, y)
    except ValueError:
        raise ValueError(f"Координаты должны быть числами: {coord_str}")


def main():
    parser = argparse.ArgumentParser(
        description="Добавление облачков с текстом к изображению",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  
  python script.py --text1 "Привет!" --text2 "Как дела?" --head1 "100,500" --head2 "700,500" --output comic.png
  python script.py --image-path scene.jpg --text1 "Смотри!" --head1 "200,300" --output result.jpg
  python script.py --image-path scene.jpg --text1 "Текст" --head1 "150,400" --font-path "comic.ttf" --max-bubble-width 300

Формат координат: 'x,y' или '(x,y)'
        """
    )

    # Основные параметры изображения
    parser.add_argument("--image-path", help="Путь к исходному изображению")
    parser.add_argument("--width", type=int, default=800, help="Ширина холста")
    parser.add_argument("--height", type=int, default=600, help="Высота холста")
    parser.add_argument("--bg-color", default="lightblue", help="Цвет фона холста")

    # Параметры облаков
    parser.add_argument("--text1", default="", help="Текст для первого персонажа")
    parser.add_argument("--text2", default="", help="Текст для второго персонажа")
    parser.add_argument("--head1", help="Координаты головы первого персонажа")
    parser.add_argument("--head2", help="Координаты головы второго персонажа")

    parser.add_argument("--font-path", help="Путь к файлу шрифта")
    parser.add_argument("--max-bubble-width", type=int, default=200)
    parser.add_argument("--min-font-size", type=int, default=6)

    parser.add_argument("--output", default="output.png")

    args = parser.parse_args()

    # Создание изображения
    if args.image_path:
        if not os.path.isfile(args.image_path):
            print(f"Файл изображения не найден: {args.image_path}", file=sys.stderr)
            sys.exit(1)
        try:
            image = Image.open(args.image_path).convert('RGB')
        except Exception as e:
            print(f"Ошибка загрузки изображения: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        image = Image.new('RGB', (args.width, args.height), color=args.bg_color)

    # Формируем список облаков
    bubbles = []
    if args.text1.strip() and args.head1:
        bubbles.append({
            "text": args.text1,
            "head_coords": parse_coords(args.head1),
            "font_path": args.font_path,
            "MAX_BUBBLE_WIDTH": args.max_bubble_width,
            "MIN_FONT_SIZE": args.min_font_size
        })
    if args.text2.strip() and args.head2:
        bubbles.append({
            "text": args.text2,
            "head_coords": parse_coords(args.head2),
            "font_path": args.font_path,
            "MAX_BUBBLE_WIDTH": args.max_bubble_width,
            "MIN_FONT_SIZE": args.min_font_size
        })

    # Если облаков нет, создаем простой холст
    if not bubbles and not args.image_path:
        print("Создан пустой холст (не указаны ни image-path, ни текст)")

    # Расставляем облака без наложения текстов
    if bubbles:
        result_image = add_speech_bubbles_multiple(image, bubbles)
    else:
        result_image = image

    # Сохраняем результат
    try:
        result_image.save(args.output)
        print(f"Изображение сохранено: {args.output}")
    except Exception as e:
        print(f"Ошибка сохранения: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
