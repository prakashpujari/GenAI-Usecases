import os
from typing import List, Dict
from PyPDF2 import PdfReader
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
    except ImportError:
        # Fallback to manual text splitting if langchain is not available
        RecursiveCharacterTextSplitter = None

class DocumentLoader:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        if RecursiveCharacterTextSplitter is not None:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
            )
        else:
            # Simple fallback splitter
            self.text_splitter = None
    
    def _simple_split(self, text: str) -> List[str]:
        """Simple text splitter fallback if langchain is not available."""
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += self.chunk_size - self.chunk_overlap
        
        return chunks

    def load_pdfs(self, directory: str) -> List[Dict]:
        """Load PDFs from a directory and return list of text chunks with metadata.

        Each chunk is a dict: {"text": str, "meta": {"source": filename, "page": page_number}}
        """
        text_chunks = []

        # If directory doesn't exist, return empty list instead of throwing
        if not os.path.exists(directory):
            return text_chunks

        for filename in os.listdir(directory):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(directory, filename)
                try:
                    pdf = PdfReader(pdf_path)
                except Exception:
                    # skip files that can't be read as PDFs
                    continue

                # Extract text from each page and split per-page so we can
                # attach page-level metadata to each chunk.
                for page_idx, page in enumerate(pdf.pages, start=1):
                    try:
                        page_text = page.extract_text() or ""
                    except Exception:
                        page_text = ""
                    if not page_text.strip():
                        continue

                    # Split the page text into chunks and attach metadata
                    if self.text_splitter is not None:
                        chunks = self.text_splitter.split_text(page_text)
                    else:
                        chunks = self._simple_split(page_text)
                    
                    for c in chunks:
                        text_chunks.append({
                            "text": c,
                            "meta": {"source": filename, "page": page_idx}
                        })

        return text_chunks