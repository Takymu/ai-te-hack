import os
import sys
from datetime import datetime
from urllib.parse import quote, urlencode

import requests

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


def get_content(resp: requests.Response, output_prefix: str = None) -> str:
    ct = resp.headers.get("Content-Type", "")
    ext = infer_ext_from_content_type(ct)
    return resp.content, ext


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
        prompt_file: Path to a file containing the prompt
        width: Image width
        height: Image height
        seed: Random seed for generation
        model: Model identifier (optional)
        output: Output filename without extension
    
    Returns:
        Path to the saved image file
    """
    prompt_text = prompt
    if (not prompt_text) and prompt_file:
        if not os.path.isfile(prompt_file):
            print(f"Файл промпта не найден: {prompt_file}", file=sys.stderr)
            sys.exit(1)
        with open(prompt_file, "r", encoding="utf-8") as pf:
            prompt_text = pf.read().strip()
    if not prompt_text:
        print("Укажите prompt или prompt_file", file=sys.stderr)
        sys.exit(1)

    url = build_url(prompt_text, width=width, height=height, seed=seed, model=model)

    try:
        resp = requests.get(url, timeout=300)
    except requests.RequestException as e:
        print(f"Сетевая ошибка: {e}", file=sys.stderr)
        sys.exit(2)

    if not resp.ok:
        print(f"HTTP ошибка: {resp.status_code} {resp.text[:2000]}", file=sys.stderr)
        sys.exit(3)

    out = get_content(resp, output)
    return out


if __name__ == "__main__":

    result = generate_image(
        prompt="path/to/prompt.txt",
        width=832,
        height=512,
        seed=42,
        output="сгенерированная-картинка"
    )
    print(f"Сохранено: {result}")