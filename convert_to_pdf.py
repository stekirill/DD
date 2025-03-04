import os
import pypandoc
import pdfkit

def merge_md_to_pdf(directory, output_pdf):
    md_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    
    combined_content = ""
    for md_file in md_files:
        with open(md_file, 'r', encoding='utf-8') as file:
            combined_content += file.read() + "\n\n"

    html_content = pypandoc.convert_text(combined_content, 'html', format='md')
    html_content = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: "DejaVu Sans", sans-serif;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    with open('temp.html', 'w', encoding='utf-8') as temp_file:
        temp_file.write(html_content)
    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    pdfkit.from_string(html_content, output_pdf, configuration=config, options={'encoding': 'UTF-8'})

directory_with_md = "Документация"
output_pdf_file = "docs.pdf"

merge_md_to_pdf(directory_with_md, output_pdf_file)
