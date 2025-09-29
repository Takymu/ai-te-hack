import os
import sys
from datetime import datetime
from urllib.parse import quote, urlencode

import requests
from io import BytesIO
try:
    from PIL import Image, ImageDraw, ImageFont  # optional
    _HAVE_PIL = True
except Exception:
    Image = ImageDraw = ImageFont = None
    _HAVE_PIL = False
import time

API_BASE = "https://image.pollinations.ai/prompt/"


def build_url(prompt: str, width: int = None, height: int = None, seed: int = None, model: str = None) -> str:
    encoded_prompt = quote(prompt, safe="")
    url = API_BASE + encoded_prompt
    params = {}
    if width:
        params["width"] = width
    if height:
        params["height"] = height
    if seed is not None:
        params["seed"] = seed
    if model:
        params["model"] = model
    if params:
        url += ("?" + urlencode(params))
    return url


def infer_ext_from_content_type(ct: str) -> str:
    if not ct:
        return ".jpg"
    ct = ct.lower()
    if "png" in ct:
        return ".png"
    if "jpeg" in ct or "jpg" in ct:
        return ".jpg"
    if "webp" in ct:
        return ".webp"
    return ".jpg"


def get_content(resp: requests.Response, output_prefix: str = None):
    ct = resp.headers.get("Content-Type", "")
    ext = infer_ext_from_content_type(ct)
    return resp.content, ext


def _placeholder_image(prompt: str) -> bytes:
    """Return a minimal PNG placeholder. Uses PIL if available; otherwise a built-in PNG bytes."""
    if _HAVE_PIL:
        width, height = 832, 512
        img = Image.new('RGB', (width, height), color=(240, 240, 240))
        draw = ImageDraw.Draw(img)
        text = "Image unavailable\nRetry later"
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except Exception:
            font = ImageFont.load_default()
        try:
            bbox = draw.multiline_textbbox((0, 0), text, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        except Exception:
            # Fallback if multiline_textbbox is missing (older Pillow)
            tw, th = draw.textsize(text, font=font)
        x = (width - tw) // 2
        y = (height - th) // 2
        draw.multiline_text((x, y), text, fill=(80, 80, 80), font=font, align="center")
        buf = BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()

    # Built-in tiny gray 1x1 PNG bytes (no PIL required)
    return (b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
            b"\x00\x00\x00\x0cIDAT\x08\x99c\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\x18\xdd\x8d\xb1\x00\x00\x00\x00IEND\xaeB`\x82")


def generate_image(
    prompt: str = None,
    prompt_file: str = None,
    width: int = None,
    height: int = None,
    seed: int = None,
    model: str = None,
    output: str = None
) -> str:
    """
    Generate an image from a prompt or prompt file using the Pollinations API.
    
    Args:
        prompt: Text description for image generation
{{ ... }}
    
    Returns:
        Path to the saved image file
    """
    prompt_text = prompt
    if (not prompt_text) and prompt_file:
        if not os.path.isfile(prompt_file):
            raise FileNotFoundError(f"Файл промпта не найден: {prompt_file}")
        with open(prompt_file, "r", encoding="utf-8") as pf:
            prompt_text = pf.read().strip()
    if not prompt_text:
        raise ValueError("Укажите prompt или prompt_file")

    url = build_url(prompt_text, width=width, height=height, seed=seed, model=model)

    # Ретраи при сетевых сбоях
    attempts = 3
    last_exc = None
    for attempt in range(1, attempts + 1):
        try:
            resp = requests.get(url, timeout=45)
            if resp.ok:
                return get_content(resp, output)
            last_exc = RuntimeError(f"HTTP ошибка: {resp.status_code}")
        except Exception as e:
            last_exc = e
        # экспоненциальная пауза
        time.sleep(1.5 * attempt)

    # Если все попытки не удались — возвращаем плейсхолдер
    print(f"Сетевая ошибка генерации изображения: {last_exc}", file=sys.stderr)
    return _placeholder_image(prompt_text), ".png"


if __name__ == "__main__":

    result = generate_image(
        width=832,
        height=512,
        seed=42,
        output="сгенерированная-картинка"
    )
    print(f"Сохранено: {result}")