import os
import pypandoc
import pdfkit
import re
import shutil
import base64
import mimetypes
from pathlib import Path


pypandoc.download_pandoc()


def find_image_file(image_name):
    """Поиск изображения в директории media и его поддиректориях"""
    media_dir = os.path.join(os.getcwd(), 'media')
    
    # Сначала проверяем, есть ли файл непосредственно в папке media
    direct_path = os.path.join(media_dir, image_name)
    if os.path.exists(direct_path):
        return direct_path
    
    # Если не найден, ищем рекурсивно во всех поддиректориях
    for root, dirs, files in os.walk(media_dir):
        for file in files:
            if file == image_name:
                return os.path.join(root, file)
    
    # Проверяем также в директориях Админка и News, которые видны в структуре проекта
    admin_path = os.path.join(media_dir, 'Админка')
    if os.path.exists(admin_path):
        for root, dirs, files in os.walk(admin_path):
            for file in files:
                if file == image_name:
                    return os.path.join(root, file)
    
    news_path = os.path.join(media_dir, 'News')
    if os.path.exists(news_path):
        for root, dirs, files in os.walk(news_path):
            for file in files:
                if file == image_name:
                    return os.path.join(root, file)
    
    return None


def image_to_base64(image_path):
    """Конвертирует изображение в base64"""
    if not os.path.exists(image_path):
        return None
    
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        mime_type = 'image/png'  # Используем PNG как формат по умолчанию
    
    with open(image_path, 'rb') as img_file:
        encoded = base64.b64encode(img_file.read()).decode('utf-8')
    
    return f"data:{mime_type};base64,{encoded}"


def process_image_tags(content):
    """Обрабатывает Obsidian теги изображений и заменяет их на HTML img теги с base64 данными"""
    def replace_image(match):
        image_name = match.group(1)
        image_path = find_image_file(image_name)
        if image_path:
            base64_data = image_to_base64(image_path)
            if base64_data:
                return f'<img src="{base64_data}" alt="{image_name}" />'
        # Если изображение не найдено, оставляем оригинальный тег
        return f'![{image_name}](not_found_{image_name})'
    
    # Заменяем Obsidian-стиль ![[image.png]] на HTML img теги с base64
    processed_content = re.sub(r'!\[\[(.*?)\]\]', replace_image, content)
    return processed_content


def fix_mixed_syntax(content):
    """Исправляет смешанный синтаксис HTML и Markdown"""
    # Исправляем случаи, когда Markdown заголовки находятся внутри HTML тегов
    # Например: <li><strong>FeedBack</strong> ### 2) Описание таблиц</li>
    content = re.sub(r'(</strong>)\s+(#{1,6}\s+[^<]+)(<)', r'\1</li>\n\n\2\n\n<li>\3', content)
    
    # Исправляем случаи с ### Referral</li>
    content = re.sub(r'(#{1,6}\s+[^<]+)(</li>)', r'\1\n\2', content)
    
    # Ищем другие случаи, когда Markdown синтаксис внутри HTML тегов
    content = re.sub(r'(<li>.*?)(#{1,6}\s+[^<]+)(.*?</li>)', r'\1\3\n\n\2', content)
    
    return content


def merge_md_to_pdf(directory, output_pdf):
    md_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    
    if not md_files:
        print(f"ПРЕДУПРЕЖДЕНИЕ: В директории '{directory}' не найдено Markdown файлов.")
        return False
    
    combined_content = ""
    for md_file in md_files:
        with open(md_file, 'r', encoding='utf-8') as file:
            content = file.read()
            # Обрабатываем теги изображений
            content = process_image_tags(content)
            combined_content += content + "\n\n"
    
    # Конвертируем в HTML
    try:
        html_content = pypandoc.convert_text(combined_content, 'html', format='markdown')
        
        # Исправляем смешанный синтаксис в сгенерированном HTML
        html_content = fix_mixed_syntax(html_content)
        
        html_content = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: "DejaVu Sans", sans-serif;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Сохраняем HTML для отладки
        html_temp_file = f"temp_{os.path.basename(output_pdf).replace('.pdf', '.html')}"
        with open(html_temp_file, 'w', encoding='utf-8') as temp_file:
            temp_file.write(html_content)
        
        try:
            # Пытаемся найти wkhtmltopdf автоматически
            config = None
            wkhtmltopdf_path = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
            if os.path.exists(wkhtmltopdf_path):
                config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
            
            pdfkit.from_string(
                html_content, 
                output_pdf, 
                configuration=config, 
                options={
                    'encoding': 'UTF-8',
                    'enable-local-file-access': True
                }
            )
            print(f"PDF успешно создан: {output_pdf}")
            return True
        except Exception as e:
            print(f"Ошибка при создании PDF: {e}")
            print("Проверьте, установлен ли wkhtmltopdf и корректен ли путь к нему")
            return False
    except Exception as e:
        print(f"Ошибка при конвертации Markdown в HTML: {e}")
        return False


def create_multiple_pdfs():
    """Создает несколько PDF из разных директорий"""
    conversions = [
        {
            "directory": os.path.join("Документация", "Сервисы", "Админка", "Информация для маркетологов"),
            "output": "админка_маркетинг.pdf"
        },
        {
            "directory": os.path.join("Документация", "Сервисы", "Админка", "Информация для бэкэнда Админки"),
            "output": "админка_бэкенд.pdf"
        },
        # {
        #     "directory": os.path.join("Документация", "Сервисы", "News", "Информация для маркетологов"),
        #     "output": "news_маркетинг.pdf"
        # },
        {
            "directory": os.path.join("Документация", "Сервисы", "News", "Информация для бэкэнда News"),
            "output": "news_бэкенд.pdf"
        }
    ]
    
    successful = 0
    failed = 0
    
    for conversion in conversions:
        directory = conversion["directory"]
        output = conversion["output"]
        
        print(f"\n=== Обработка: {directory} -> {output} ===")
        
        if not os.path.exists(directory):
            print(f"ОШИБКА: Директория '{directory}' не существует. Пропускаем.")
            failed += 1
            continue
        
        if merge_md_to_pdf(directory, output):
            successful += 1
        else:
            failed += 1
    
    print(f"\n=== Итоги конвертации ===")
    print(f"Успешно: {successful}")
    print(f"С ошибками: {failed}")
    print(f"Всего: {successful + failed}")


# Проверяем, запущен ли скрипт напрямую
if __name__ == "__main__":
    # Спрашиваем у пользователя, какой режим использовать
    print("Выберите режим работы:")
    print("1. Создать один PDF из всей документации")
    print("2. Создать несколько PDF из разных директорий")
    
    try:
        choice = int(input("Введите номер режима (1 или 2): "))
        
        if choice == 1:
            directory_with_md = "Документация"
            output_pdf_file = "docs.pdf"
            
            if not os.path.exists(directory_with_md):
                print(f"ОШИБКА: Директория '{directory_with_md}' не найдена.")
                directory_with_md = input("Введите путь к директории с Markdown файлами: ")
            
            merge_md_to_pdf(directory_with_md, output_pdf_file)
            
        elif choice == 2:
            create_multiple_pdfs()
            
        else:
            print("Неверный выбор. Пожалуйста, выберите 1 или 2.")
            
    except ValueError:
        print("Ошибка ввода. Пожалуйста, введите число.")
        
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем.")
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")
