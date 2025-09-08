from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage
import json

class AgentState(TypedDict):
    messages: List[BaseMessage]
    query: str
    data_file: Optional[str]
    data_sample: Optional[Dict]
    analysis_result: Optional[Dict]
    visualizations: Optional[List[Dict]]
    business_impact: Optional[Dict]
    recommendations: Optional[List[str]]
    current_step: str
    error: Optional[str]

class DataAnalysisWorkflow:
    def __init__(self):
        self.workflow = StateGraph(AgentState)
        self._setup_nodes()
        self._setup_edges()
        self.app = self.workflow.compile()
    
    def _setup_nodes(self):
        from backend.langgraph.nodes import (
            parse_query,
            load_data,
            analyze_data,
            generate_visualizations,
            extract_business_impact,
            format_response
        )
        
        self.workflow.add_node("parse_query", parse_query)
        self.workflow.add_node("load_data", load_data)
        self.workflow.add_node("analyze_data", analyze_data)
        self.workflow.add_node("generate_visualizations", generate_visualizations)
        self.workflow.add_node("extract_business_impact", extract_business_impact)
        self.workflow.add_node("format_response", format_response)
    
    def _setup_edges(self):
        self.workflow.set_entry_point("parse_query")
        
        self.workflow.add_edge("parse_query", "load_data")
        self.workflow.add_edge("load_data", "analyze_data")
        self.workflow.add_edge("analyze_data", "generate_visualizations")
        self.workflow.add_edge("generate_visualizations", "extract_business_impact")
        self.workflow.add_edge("extract_business_impact", "format_response")
        self.workflow.add_edge("format_response", END)
    
    async def run(self, query: str, data_file: str = None):
        """
        Execute the workflow with streaming support
        """
        initial_state = {
            "query": query,
            "data_file": data_file,
            "messages": [],
            "current_step": "starting"
        }
        
        async for state in self.app.astream(initial_state):
            yield self._format_stream_event(state)
    
    def _format_stream_event(self, state: Dict) -> Dict:
        """
        Format state updates for streaming to frontend
        """
        return {
            "step": state.get("current_step", ""),
            "analysis": state.get("analysis_result"),
            "visualizations": state.get("visualizations"),
            "business_impact": state.get("business_impact"),
            "recommendations": state.get("recommendations"),
            "error": state.get("error")
        }