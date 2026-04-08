import fitz
from ocr_client import send_to_ocr

def detect_page_type(page):
    text = page.get_text("text")
    word_count = len(text.split())

    images = page.get_images()

    if word_count > 30:
        return "text"
    
    if len(images) > 0 and word_count < 10:
        return "image"
    
    return "mixed"


# Convert page to pdf_bytes
def page_to_pdf_bytes(page):
    doc = page.parent
    new_doc = fitz.open()
    new_doc.insert_pdf(doc,from_page=page.number,to_page=page.number)
    return new_doc.tobytes()


def table_to_markdown(table):
    if not table:
        return "No Table"
    
    md = []

    header = "| " + " | ".join([str(cell) if cell else "" for cell in table[0]]) + " |"
    separator = "| " + " | ".join(["------"]*len(table[0])) + " |"
    md.append(header)
    md.append(separator)

    for row in table[1:]:
        row_text = "| " + " | ".join([str(cell) if cell else "" for cell in row]) + " |"
        md.append(row_text)

    return "\n".join(md) 


def extract_table_from_page(page):
    markdown_tables = []
    tables = page.find_tables()
    
    if not tables:
        return "No Table"
    
    for table in tables.tables:
        data = table.extract()
        if not data:
            continue
        md = table_to_markdown(data)
        if md:
            markdown_tables.append(md)

    return "\n\n".join(markdown_tables)   


def process_text_page(page):
    text = page.get_text("text") or ""
    tables_md = extract_table_from_page(page) or ""
    combined = text
    if tables_md:
        combined += "\n\n#### TABLES \n\n" + tables_md
    return combined

def process_image_page(page):
    # pix = page.get_pixmap()
    # image_bytes = pix.tobytes()
    pdf_bytes = page_to_pdf_bytes(page)
    # Main issue, if entire document is scanned
    # ocr_text = send_to_ocr(image_bytes=image_bytes)
    ocr_text = send_to_ocr(pdf_bytes=pdf_bytes)

    return ocr_text


def process_mixed_page(page):
    text = page.get_text("text") or ""
    tables_md = extract_table_from_page(page)
    # pix = page.get_pixmap()
    # image_bytes = pix.tobytes()
    pdf_bytes = page_to_pdf_bytes(page)
    # ocr_text = send_to_ocr(image_bytes=image_bytes)
    ocr_text = send_to_ocr(pdf_bytes=pdf_bytes)
    combined = text
    if tables_md:
        combined += "\n\n#### TABLES\n\n" + tables_md

    combined += "\n\n#### OCR TEXT\n\n" + ocr_text    
    return combined


def merge_pages(pages):
    full_text = ""

    for p in pages:
        page_text = p.get("text") or ""
        full_text += f"\n\n------- PAGE {p['page']} ({p['type']}) --------\n\n"
        full_text += page_text

    return full_text    

def process_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    page_outputs = []

    for page_num, page in enumerate(doc):
        page_type = detect_page_type(page)
        if page_type == "text":
            text = process_text_page(page)

        elif page_type == "image":
            text = process_image_page(page)
        else:
            text = process_mixed_page(page)

        page_outputs.append({
            "page":page_num + 1,
            "text": text,
            "type":page_type
        })       

    return merge_pages(page_outputs)    