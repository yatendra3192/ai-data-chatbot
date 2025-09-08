from deepagents import create_deep_agent
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from backend.config.settings import settings

class DataAnalystDeepAgent:
    def __init__(self):
        self.model = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.1,
            streaming=True
        )
        
        self.instructions = """
        You are an expert data analyst AI assistant. Your role is to:
        1. Analyze CSV data with millions of rows efficiently
        2. Generate meaningful business insights
        3. Identify patterns, trends, and anomalies
        4. Provide actionable recommendations
        5. Create appropriate visualizations for the data
        
        When analyzing data:
        - Focus on key business metrics
        - Identify top performers and underperformers
        - Calculate important statistics
        - Suggest risk mitigation strategies
        - Provide revenue optimization recommendations
        
        Always structure your analysis to include:
        - Summary of findings
        - Key recommendations
        - Business impact assessment
        - Suggested visualizations
        """
        
        self.agent = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        from backend.langgraph.tools import (
            calculate_statistics,
            filter_data,
            aggregate_data,
            detect_anomalies,
            generate_sql_query,
            analyze_trends
        )
        
        tools = [
            calculate_statistics,
            filter_data,
            aggregate_data,
            detect_anomalies,
            generate_sql_query,
            analyze_trends
        ]
        
        self.agent = create_deep_agent(
            tools=tools,
            instructions=self.instructions,
            model=self.model,
            builtin_tools=["write_todos", "read_file", "write_file"]
        )
    
    def analyze(self, query: str, data_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform deep analysis on the query with data context
        """
        messages = [
            {
                "role": "system",
                "content": f"Data context: {data_context}"
            },
            {
                "role": "user",
                "content": query
            }
        ]
        
        result = self.agent.invoke({"messages": messages})
        
        return self._parse_analysis_result(result)
    
    def _parse_analysis_result(self, result: Dict) -> Dict[str, Any]:
        """
        Parse the agent result into structured format
        """
        return {
            "summary": result.get("summary", ""),
            "recommendations": result.get("recommendations", []),
            "business_impact": result.get("business_impact", ""),
            "visualizations": result.get("visualizations", []),
            "metrics": result.get("metrics", {})
        }

class BusinessInsightsAgent:
    def __init__(self):
        self.model = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.2
        )
        
        self.instructions = """
        You are a business strategy expert. Focus on:
        - Identifying revenue opportunities
        - Risk assessment and mitigation
        - Customer segmentation insights
        - Product performance analysis
        - Market trend identification
        """
        
    def generate_insights(self, data_analysis: Dict) -> Dict[str, Any]:
        """
        Generate business insights from data analysis
        """
        prompt = f"""
        Based on this data analysis: {data_analysis}
        
        Provide:
        1. Key business opportunities
        2. Risk factors to consider
        3. Strategic recommendations
        4. Expected business impact (revenue/cost)
        """
        
        response = self.model.invoke(prompt)
        return self._format_insights(response)
    
    def _format_insights(self, response) -> Dict[str, Any]:
        return {
            "opportunities": [],
            "risks": [],
            "recommendations": [],
            "impact_assessment": ""
        }