"""
LangGraph Orchestrator - Multi-agent state machine for FinSight AI.
"""
from typing import Dict, TypedDict
from langgraph.graph import StateGraph, END
from models.schemas import AgentState
from agents.market_data_agent import market_data_agent
from agents.news_sentiment_agent import news_sentiment_agent
from agents.research_agent import research_agent
from agents.forecast_agent import forecast_agent
from agents.report_agent import report_agent


def create_workflow() -> StateGraph:
    """
    Create the LangGraph workflow for multi-agent analysis.
    
    Returns:
        Compiled StateGraph
    """
    # Create state graph
    workflow = StateGraph(AgentState)
    
    # Add nodes (agents) - node names must not conflict with state keys
    workflow.add_node("fetch_market_data", market_data_agent)
    workflow.add_node("analyze_sentiment", news_sentiment_agent)
    workflow.add_node("research_company", research_agent)
    workflow.add_node("generate_forecast", forecast_agent)
    workflow.add_node("create_report", report_agent)
    
    # Define edges (sequential flow)
    workflow.set_entry_point("fetch_market_data")
    workflow.add_edge("fetch_market_data", "analyze_sentiment")
    workflow.add_edge("analyze_sentiment", "research_company")
    workflow.add_edge("research_company", "generate_forecast")
    workflow.add_edge("generate_forecast", "create_report")
    workflow.add_edge("create_report", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app


def run_analysis(company_name: str) -> AgentState:
    """
    Run the complete multi-agent analysis for a company.
    
    Args:
        company_name: Name of the company to analyze
        
    Returns:
        Final agent state with all analysis complete
    """
    # Create workflow
    app = create_workflow()
    
    # Initialize state
    initial_state: AgentState = {
        "company_name": company_name,
        "ticker": "",
        "messages": [f"🚀 Starting analysis for {company_name}..."],
        "current_agent": "orchestrator"
    }
    
    # Run the workflow
    final_state = app.invoke(initial_state)
    
    return final_state
