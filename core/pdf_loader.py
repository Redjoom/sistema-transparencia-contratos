import fitz


def load_pdf(path):
    doc = fitz.open(path)
    pages = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        blocks = page.get_text("blocks")
        pages.append({
            "number": page_num + 1,
            "text": text,
            "blocks": blocks,
            "width": page.rect.width,
            "height": page.rect.height,
            "page": page,
        })
    return pages, doc


def unload_pdf(doc):
    doc.close()
