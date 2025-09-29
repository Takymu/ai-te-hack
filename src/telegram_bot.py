import os
import tempfile
import traceback
import io

import telebot
from dotenv import load_dotenv, find_dotenv
from PIL import Image

from .pipeline import generate_comic_from_pdf
try:
    from openai import AuthenticationError, RateLimitError, NotFoundError
except Exception:
    AuthenticationError = RateLimitError = NotFoundError = Exception


def get_bot() -> telebot.TeleBot:
    try:
        load_dotenv(find_dotenv())
    except Exception:
        pass

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Не задан TELEGRAM_BOT_TOKEN в .env или окружении")

    bot = telebot.TeleBot(token, parse_mode=None)
    return bot


bot = get_bot()


def _prepare_image_for_telegram(png_path: str) -> str:
    """Конвертирует PNG в более лёгкий JPEG (и даунскейлит, если очень большое изображение).
    Возвращает путь к временному JPEG-файлу. При ошибке возвращает исходный путь."""
    try:
        with Image.open(png_path) as im:
            im = im.convert('RGB')
            max_side = 2048
            w, h = im.size
            if max(w, h) > max_side:
                scale = max_side / float(max(w, h))
                im = im.resize((int(w*scale), int(h*scale)), Image.LANCZOS)

            fd, tmp_jpg = tempfile.mkstemp(suffix='.jpg')
            os.close(fd)
            im.save(tmp_jpg, format='JPEG', quality=85, optimize=True)
            return tmp_jpg
    except Exception:
        pass
    return png_path


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(
        message,
        "Приветствую Вас! Отправьте PDF-файл с документом. Я верну сгенерированный комикс в PNG."
    )


@bot.message_handler(content_types=['document'])
def handle_document(message):
    try:
        doc = message.document
        if not doc.file_name.lower().endswith('.pdf'):
            bot.reply_to(message, "Пожалуйста, отправьте файл в формате PDF.")
            return

        # Скачиваем PDF во временный файл
        file_info = bot.get_file(doc.file_id)
        downloaded = bot.download_file(file_info.file_path)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            tmp_pdf.write(downloaded)
            tmp_pdf_path = tmp_pdf.name

        bot.reply_to(message, "Документ получен. Начинаю генерацию комикса, это может занять несколько минут, наберитесь терпения, пожалуйста...")

        # Генерация комикса
        output_path = generate_comic_from_pdf(tmp_pdf_path)

        # Подготовим файл к отправке (сжатие/даунскейл)
        send_path = _prepare_image_for_telegram(output_path)

        # Отправляем результат с увеличенным таймаутом и ретраями
        attempts = 3
        last_err = None
        for _ in range(attempts):
            try:
                with open(send_path, 'rb') as f:
                    bot.send_document(
                        message.chat.id,
                        f,
                        visible_file_name=os.path.basename(send_path),
                        timeout=300,
                    )
                last_err = None
                break
            except Exception as e:
                last_err = e
        if last_err:
            raise last_err

    except Exception as e:
        # Логи для разработчика
        traceback.print_exc()

        # Специальные сообщения для частых кодов ошибок OpenRouter/OpenAI
        if isinstance(e, NotFoundError) or 'Error code: 404' in str(e):
            bot.reply_to(
                message,
                "Упс, что-то пошло не так. Возможно, Ваш документ слишком большой, к сожалению, нам не удаётся создать по нему комикс."
            )
            return

        if isinstance(e, RateLimitError) or 'Error code: 429' in str(e):
            bot.reply_to(
                message,
                "Упс, на сегодня количество бесплатных генераций комиксов исчерпано, попробуйте загрузить Ваш документ завтра."
            )
            return

        if isinstance(e, AuthenticationError) or 'Error code: 401' in str(e):
            bot.reply_to(
                message,
                "Упс, у сервиса временные неприятности, попробуйте обратиться к нам с Вашим документом позже."
            )
            return

        # Общее сообщение по умолчанию
        bot.reply_to(
            message,
            "Упс, что-то пошло не так. Возможно, Ваш документ слишком большой, к сожалению, нам не удаётся создать по нему комикс."
        )


if __name__ == '__main__':
    print("Telegram bot is running. Press Ctrl+C to stop.")
    bot.infinity_polling(skip_pending=True)
