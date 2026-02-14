"""
Research Agent - Performs agentic RAG or uses LLM knowledge as fallback.
"""
import os
from typing import List
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from models.schemas import AgentState, ResearchInsight
from rag.ingest import load_pdfs, split_documents
from rag.vector_store import create_vector_store, load_vector_store
from rag.hybrid_search import HybridSearchRetriever

load_dotenv()

# Global RAG components cache
_vector_store = None
_hybrid_retriever = None
_rag_initialized = False


def initialize_rag():
    """Initialize RAG system if PDFs are available."""
    global _vector_store, _hybrid_retriever, _rag_initialized
    
    if _rag_initialized:
        return _vector_store, _hybrid_retriever
    
    try:
        # Try to load existing vector store
        vector_store_path = "data/vector_store"
        _vector_store = load_vector_store(vector_store_path)
        
        if _vector_store is None:
            # Create new vector store from PDFs
            documents = load_pdfs("data/reports/")
            if documents:
                split_docs = split_documents(documents)
                _vector_store = create_vector_store(split_docs)
                
                if _vector_store:
                    _hybrid_retriever = HybridSearchRetriever(_vector_store, split_docs)
        
        _rag_initialized = True
        return _vector_store, _hybrid_retriever
        
    except Exception as e:
        print(f"⚠️ RAG initialization error: {str(e)}")
        _rag_initialized = True
        return None, None


def research_agent(state: AgentState) -> AgentState:
    """
    Perform research using RAG or LLM knowledge.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with research insights
    """
    try:
        company_name = state.get("company_name", "")
        ticker = state.get("ticker", "")
        messages = state.get("messages", [])
        messages.append("🔄 Research Agent: Analyzing company...")
        
        # Initialize RAG
        vector_store, hybrid_retriever = initialize_rag()
        
        # Initialize Gemini LLM
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            raise ValueError("Google API key not configured")
        
        llm = ChatGoogleGenerativeAI(
            model="models/gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.3
        )
        
        # Generate research queries (agentic approach)
        research_queries = [
            f"{company_name} revenue growth and financial performance",
            f"{company_name} major business risks and challenges",
            f"{company_name} management outlook and future guidance",
            f"{company_name} competitive position and market share"
        ]
        
        # Retrieve relevant information
        context = ""
        if hybrid_retriever:
            messages.append("📚 Research Agent: Using RAG retrieval...")
            for query in research_queries:
                docs = hybrid_retriever.retrieve(query, k=2)
                for doc in docs:
                    context += doc.page_content + "\n\n"
        
        # Generate insights using LLM
        if context:
            prompt = f"""You are a senior financial analyst. Based on the following information about {company_name} ({ticker}), 
provide a comprehensive research analysis.

Context from reports:
{context[:3000]}

Provide:
1. Key findings (3-5 bullet points)
2. Revenue growth analysis
3. Major risks (3-5 points)
4. Management outlook

Format your response as JSON with keys: key_findings (list), revenue_growth (string), major_risks (list), management_outlook (string)
"""
        else:
            messages.append("💡 Research Agent: Using LLM knowledge (no PDFs available)...")
            prompt = f"""You are a senior financial analyst. Provide a research analysis for {company_name} ({ticker}), 
a major Indian company. Based on your general knowledge:

Provide:
1. Key findings about the company (3-5 bullet points)
2. Revenue growth analysis
3. Major risks (3-5 points)
4. Management outlook and strategy

Format your response as JSON with keys: key_findings (list), revenue_growth (string), major_risks (list), management_outlook (string)
"""
        
        # Get structured output
        structured_llm = llm.with_structured_output(ResearchInsight)
        research_insight = structured_llm.invoke(prompt)
        
        messages.append(f"✅ Research Agent: Analysis complete - {len(research_insight.key_findings)} key findings")
        
        return {
            **state,
            "research": research_insight,
            "messages": messages,
            "current_agent": "research"
        }
        
    except Exception as e:
        messages = state.get("messages", [])
        messages.append(f"❌ Research Agent Error: {str(e)}")
        
        # Fallback research insight
        fallback_research = ResearchInsight(
            key_findings=[
                f"{state.get('company_name', 'Company')} is a major player in its sector",
                "Strong market position in India",
                "Diversified business portfolio"
            ],
            revenue_growth="Steady growth trajectory expected",
            major_risks=[
                "Market volatility",
                "Regulatory changes",
                "Competition"
            ],
            management_outlook="Positive outlook with focus on expansion"
        )
        
        return {
            **state,
            "research": fallback_research,
            "messages": messages,
            "error": str(e)
        }
