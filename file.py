

import qdrant
import chunker

import pymupdf # PyMuPDF for PDF handling



# Utility function to extract text from a PDF file
def extract_text_from_pdf(pdf_bytes):
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)  # Loads a specific page
        text += page.get_text("text")  # Extract text from the page
    return text