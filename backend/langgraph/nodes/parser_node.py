from typing import Dict, Any
import re

async def parse_query(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse user query to extract intent and entities
    """
    state["current_step"] = "parsing_query"
    
    query = state.get("query", "").lower()
    
    # Extract intent
    intent = _extract_intent(query)
    
    # Extract entities
    entities = _extract_entities(query)
    
    # Extract metrics
    metrics = _extract_metrics(query)
    
    state["parsed_query"] = {
        "original": state.get("query"),
        "intent": intent,
        "entities": entities,
        "metrics": metrics
    }
    
    return state

def _extract_intent(query: str) -> str:
    """
    Extract the main intent from the query
    """
    if any(word in query for word in ["show", "display", "visualize", "chart", "graph"]):
        return "visualize"
    elif any(word in query for word in ["calculate", "compute", "sum", "average", "mean"]):
        return "calculate"
    elif any(word in query for word in ["compare", "versus", "vs", "between"]):
        return "compare"
    elif any(word in query for word in ["trend", "pattern", "forecast", "predict"]):
        return "analyze_trend"
    elif any(word in query for word in ["top", "best", "highest", "largest"]):
        return "top_n"
    elif any(word in query for word in ["anomaly", "outlier", "unusual", "abnormal"]):
        return "detect_anomaly"
    else:
        return "general_analysis"

def _extract_entities(query: str) -> Dict[str, Any]:
    """
    Extract entities like customer, product, date ranges
    """
    entities = {}
    
    # Extract numbers
    numbers = re.findall(r'\b\d+\b', query)
    if numbers:
        entities["numbers"] = [int(n) for n in numbers]
    
    # Extract date-related terms
    date_patterns = [
        r'\b\d{4}-\d{2}-\d{2}\b',
        r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\b',
        r'\b(?:last|this|next)\s+(?:week|month|year|quarter)\b'
    ]
    
    for pattern in date_patterns:
        matches = re.findall(pattern, query, re.IGNORECASE)
        if matches:
            entities["dates"] = matches
            break
    
    # Extract business entities
    if "customer" in query:
        entities["focus"] = "customer"
    elif "product" in query:
        entities["focus"] = "product"
    elif "revenue" in query:
        entities["focus"] = "revenue"
    elif "order" in query:
        entities["focus"] = "order"
    
    return entities

def _extract_metrics(query: str) -> list:
    """
    Extract metrics mentioned in the query
    """
    metrics = []
    
    metric_keywords = {
        "revenue": ["revenue", "sales", "income"],
        "quantity": ["quantity", "amount", "volume", "units"],
        "profit": ["profit", "margin", "earnings"],
        "cost": ["cost", "expense", "spending"],
        "count": ["count", "number", "total"],
        "average": ["average", "mean", "avg"],
        "sum": ["sum", "total", "aggregate"]
    }
    
    for metric, keywords in metric_keywords.items():
        if any(keyword in query for keyword in keywords):
            metrics.append(metric)
    
    return metrics