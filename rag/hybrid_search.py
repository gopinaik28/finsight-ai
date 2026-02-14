"""
Hybrid search combining FAISS vector search with BM25 keyword search.
Uses Reciprocal Rank Fusion (RRF) to combine results.
"""
from typing import List
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from rank_bm25 import BM25Okapi


class HybridSearchRetriever:
    """
    Hybrid retriever combining dense (FAISS) and sparse (BM25) search.
    """
    
    def __init__(self, vector_store: FAISS, documents: List[Document]):
        """
        Initialize hybrid search retriever.
        
        Args:
            vector_store: FAISS vector store for semantic search
            documents: List of documents for BM25 indexing
        """
        self.vector_store = vector_store
        self.documents = documents
        
        # Create BM25 index
        tokenized_docs = [doc.page_content.lower().split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized_docs)
        
        print(f"✅ Initialized hybrid retriever with {len(documents)} documents")
    
    def retrieve(self, query: str, k: int = 5) -> List[Document]:
        """
        Retrieve documents using hybrid search (FAISS + BM25 with RRF).
        
        Args:
            query: Search query
            k: Number of documents to retrieve
            
        Returns:
            List of top-k documents
        """
        try:
            # FAISS semantic search
            vector_results = self.vector_store.similarity_search(query, k=k*2)
            
            # BM25 keyword search
            tokenized_query = query.lower().split()
            bm25_scores = self.bm25.get_scores(tokenized_query)
            bm25_top_indices = sorted(
                range(len(bm25_scores)),
                key=lambda i: bm25_scores[i],
                reverse=True
            )[:k*2]
            
            bm25_results = [self.documents[i] for i in bm25_top_indices]
            
            # Reciprocal Rank Fusion (RRF)
            rrf_scores = {}
            
            # Score vector results
            for rank, doc in enumerate(vector_results):
                doc_content = doc.page_content
                rrf_scores[doc_content] = rrf_scores.get(doc_content, 0) + 1 / (rank + 60)
            
            # Score BM25 results
            for rank, doc in enumerate(bm25_results):
                doc_content = doc.page_content
                rrf_scores[doc_content] = rrf_scores.get(doc_content, 0) + 1 / (rank + 60)
            
            # Sort by RRF score and get top-k
            sorted_docs = sorted(
                rrf_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )[:k]
            
            # Return Document objects
            result_docs = []
            for doc_content, _ in sorted_docs:
                # Find original document
                for doc in self.documents:
                    if doc.page_content == doc_content:
                        result_docs.append(doc)
                        break
            
            return result_docs
            
        except Exception as e:
            print(f"⚠️ Error in hybrid search: {str(e)}")
            # Fallback to just vector search
            return self.vector_store.similarity_search(query, k=k)
