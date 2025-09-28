import PyPDF2

def extract_text_from_pdf(file_path):
    """
    Извлекает текст из PDF-файла и возвращает его как строку.
    
    Args:
        file_path (str): Путь к PDF-файлу.
        
    Returns:
        str: Извлечённый текст из PDF.
        
    Raises:
        FileNotFoundError: Если файл не найден.
        Exception: Если произошла ошибка при обработке PDF.
    """
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            return text
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл {file_path} не найден")
    except Exception as e:
        raise Exception(f"Ошибка при обработке PDF: {str(e)}")