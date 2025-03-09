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


def merge_md_to_pdf(directory, output_pdf):
    md_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    
    combined_content = ""
    for md_file in md_files:
        with open(md_file, 'r', encoding='utf-8') as file:
            content = file.read()
            # Обрабатываем теги изображений
            content = process_image_tags(content)
            combined_content += content + "\n\n"
    
    # Конвертируем в HTML
    html_content = pypandoc.convert_text(combined_content, 'html', format='markdown')
    
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
    with open('temp.html', 'w', encoding='utf-8') as temp_file:
        temp_file.write(html_content)
    
    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    pdfkit.from_string(
        html_content, 
        output_pdf, 
        configuration=config, 
        options={
            'encoding': 'UTF-8',
            'enable-local-file-access': True
        }
    )

directory_with_md = "Документация"
output_pdf_file = "docs.pdf"

merge_md_to_pdf(directory_with_md, output_pdf_file)
