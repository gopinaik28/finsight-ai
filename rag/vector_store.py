"""
FAISS vector store management for RAG.
"""
import os
from typing import List, Optional
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()


def create_vector_store(documents: List[Document]) -> Optional[FAISS]:
    """
    Create a FAISS vector store from documents.
    
    Args:
        documents: List of documents to index
        
    Returns:
        FAISS vector store or None if creation fails
    """
    if not documents:
        print("⚠️ No documents provided for vector store creation")
        return None
    
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            print("⚠️ Google API key not configured")
            return None
        
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=api_key
        )
        
        vector_store = FAISS.from_documents(documents, embeddings)
        print(f"✅ Created vector store with {len(documents)} documents")
        
        return vector_store
    except Exception as e:
        print(f"⚠️ Error creating vector store: {str(e)}")
        return None


def load_vector_store(path: str) -> Optional[FAISS]:
    """
    Load an existing FAISS vector store from disk.
    
    Args:
        path: Path to the saved vector store
        
    Returns:
        FAISS vector store or None if loading fails
    """
    if not os.path.exists(path):
        print(f"⚠️ Vector store not found at {path}")
        return None
    
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            print("⚠️ Google API key not configured")
            return None
        
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=api_key
        )
        
        vector_store = FAISS.load_local(
            path,
            embeddings,
            allow_dangerous_deserialization=True
        )
        print(f"✅ Loaded vector store from {path}")
        
        return vector_store
    except Exception as e:
        print(f"⚠️ Error loading vector store: {str(e)}")
        return None


def save_vector_store(store: FAISS, path: str) -> bool:
    """
    Save a FAISS vector store to disk.
    
    Args:
        store: FAISS vector store to save
        path: Path where to save the vector store
        
    Returns:
        True if save was successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        store.save_local(path)
        print(f"✅ Saved vector store to {path}")
        return True
    except Exception as e:
        print(f"⚠️ Error saving vector store: {str(e)}")
        return False
