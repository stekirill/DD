import os
import pypandoc
import pdfkit

def merge_md_to_pdf(directory, output_pdf):
    # Собираем все .md файлы из директории
    md_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.md')]
    
    # Объединяем содержимое всех .md файлов
    combined_content = ""
    for md_file in md_files:
        with open(md_file, 'r', encoding='utf-8') as file:
            combined_content += file.read() + "\n\n"  # Добавляем два переноса между файлами

    # Конвертируем объединённый Markdown в HTML
    html_content = pypandoc.convert_text(combined_content, 'html', format='md')

    # Сохраняем HTML во временный файл (опционально)
    with open('temp.html', 'w', encoding='utf-8') as temp_file:
        temp_file.write(html_content)

    # Указываем путь к wkhtmltopdf вручную
    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

    # Конвертируем HTML в PDF
    pdfkit.from_string(html_content, output_pdf, configuration=config)

    print(f"PDF успешно создан: {output_pdf}")

# Укажите путь к директории с .md файлами и имя выходного PDF
directory_with_md = "Документация\\Сервисы\\News"
output_pdf_file = "output.pdf"

# Вызов функции
merge_md_to_pdf(directory_with_md, output_pdf_file)