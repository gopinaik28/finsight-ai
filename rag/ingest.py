"""
PDF ingestion and document splitting for RAG.
"""
import os
from typing import List
from PyPDF2 import PdfReader
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


def load_pdfs(directory: str = "data/reports/") -> List[Document]:
    """
    Load all PDF files from a directory.
    
    Args:
        directory: Path to directory containing PDFs
        
    Returns:
        List of Document objects
    """
    documents = []
    
    if not os.path.exists(directory):
        print(f"⚠️ Directory {directory} does not exist. Creating it...")
        os.makedirs(directory, exist_ok=True)
        return documents
    
    pdf_files = [f for f in os.listdir(directory) if f.endswith('.pdf')]
    
    if not pdf_files:
        print(f"⚠️ No PDF files found in {directory}")
        return documents
    
    for filename in pdf_files:
        filepath = os.path.join(directory, filename)
        try:
            reader = PdfReader(filepath)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            if text.strip():
                documents.append(Document(
                    page_content=text,
                    metadata={"source": filename}
                ))
                print(f"✅ Loaded {filename}")
        except Exception as e:
            print(f"⚠️ Error loading {filename}: {str(e)}")
    
    return documents


def split_documents(docs: List[Document], chunk_size: int = 1000, overlap: int = 200) -> List[Document]:
    """
    Split documents into smaller chunks for better retrieval.
    
    Args:
        docs: List of documents to split
        chunk_size: Maximum size of each chunk
        overlap: Overlap between chunks
        
    Returns:
        List of split documents
    """
    if not docs:
        return []
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    split_docs = text_splitter.split_documents(docs)
    print(f"✅ Split {len(docs)} documents into {len(split_docs)} chunks")
    
    return split_docs
