from typing import Dict, Any, List
import pandas as pd
import numpy as np
from backend.agents.deep_agent_core import DataAnalystDeepAgent

async def analyze_data(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze data using Deep Agent and generate insights
    """
    state["current_step"] = "analyzing_data"
    
    try:
        # Get data sample and query
        data_sample = state.get("data_sample", {})
        query = state.get("query", "")
        
        # Initialize Deep Agent
        analyst = DataAnalystDeepAgent()
        
        # Prepare data context
        data_context = {
            "columns": data_sample.get("columns", []),
            "row_count": data_sample.get("total_rows", 0),
            "sample_data": data_sample.get("sample", []),
            "statistics": data_sample.get("statistics", {}),
            "data_types": data_sample.get("dtypes", {})
        }
        
        # Perform deep analysis
        analysis_result = analyst.analyze(query, data_context)
        
        # Extract key metrics for dashboard
        metrics = _calculate_key_metrics(data_sample)
        
        state["analysis_result"] = {
            "summary": analysis_result.get("summary", ""),
            "metrics": metrics,
            "insights": analysis_result.get("recommendations", []),
            "patterns": _detect_patterns(data_sample)
        }
        
    except Exception as e:
        state["error"] = f"Analysis failed: {str(e)}"
    
    return state

def _calculate_key_metrics(data_sample: Dict) -> Dict[str, Any]:
    """
    Calculate key business metrics from data
    """
    metrics = {}
    
    if "dataframe" in data_sample:
        df = data_sample["dataframe"]
        
        # Revenue metrics
        if "revenue" in df.columns:
            metrics["total_revenue"] = float(df["revenue"].sum())
            metrics["avg_revenue"] = float(df["revenue"].mean())
            metrics["revenue_growth"] = _calculate_growth(df["revenue"])
        
        # Customer metrics
        if "customer_id" in df.columns:
            metrics["total_customers"] = df["customer_id"].nunique()
            metrics["top_customers"] = _get_top_customers(df)
        
        # Product metrics
        if "product" in df.columns:
            metrics["total_products"] = df["product"].nunique()
            metrics["top_products"] = _get_top_products(df)
    
    return metrics

def _detect_patterns(data_sample: Dict) -> List[Dict]:
    """
    Detect patterns and anomalies in data
    """
    patterns = []
    
    if "dataframe" in data_sample:
        df = data_sample["dataframe"]
        
        # Detect trends
        for col in df.select_dtypes(include=[np.number]).columns:
            if len(df[col]) > 10:
                trend = _detect_trend(df[col])
                if trend:
                    patterns.append({
                        "type": "trend",
                        "column": col,
                        "direction": trend
                    })
        
        # Detect outliers
        outliers = _detect_outliers(df)
        if outliers:
            patterns.extend(outliers)
    
    return patterns

def _calculate_growth(series: pd.Series) -> float:
    """Calculate growth rate"""
    if len(series) < 2:
        return 0.0
    return ((series.iloc[-1] - series.iloc[0]) / series.iloc[0] * 100)

def _get_top_customers(df: pd.DataFrame, n: int = 5) -> List[Dict]:
    """Get top customers by revenue"""
    if "revenue" in df.columns and "customer_id" in df.columns:
        top = df.groupby("customer_id")["revenue"].sum().nlargest(n)
        return [{"id": idx, "revenue": val} for idx, val in top.items()]
    return []

def _get_top_products(df: pd.DataFrame, n: int = 5) -> List[Dict]:
    """Get top products by quantity or revenue"""
    if "product" in df.columns:
        if "quantity" in df.columns:
            top = df.groupby("product")["quantity"].sum().nlargest(n)
        elif "revenue" in df.columns:
            top = df.groupby("product")["revenue"].sum().nlargest(n)
        else:
            top = df["product"].value_counts().head(n)
        return [{"name": idx, "value": val} for idx, val in top.items()]
    return []

def _detect_trend(series: pd.Series) -> str:
    """Simple trend detection"""
    if series.is_monotonic_increasing:
        return "increasing"
    elif series.is_monotonic_decreasing:
        return "decreasing"
    return ""

def _detect_outliers(df: pd.DataFrame) -> List[Dict]:
    """Detect statistical outliers"""
    outliers = []
    for col in df.select_dtypes(include=[np.number]).columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outlier_mask = (df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)
        if outlier_mask.any():
            outliers.append({
                "type": "outlier",
                "column": col,
                "count": outlier_mask.sum()
            })
    return outliers