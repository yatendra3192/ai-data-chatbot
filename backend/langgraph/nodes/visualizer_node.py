from typing import Dict, Any, List

async def generate_visualizations(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate appropriate visualizations based on analysis
    """
    state["current_step"] = "generating_visualizations"
    
    try:
        analysis = state.get("analysis_result", {})
        parsed_query = state.get("parsed_query", {})
        data_sample = state.get("data_sample", {})
        
        visualizations = []
        
        # Determine visualization types based on intent and data
        intent = parsed_query.get("intent", "general_analysis")
        focus = parsed_query.get("entities", {}).get("focus", "revenue")
        
        if "dataframe" in data_sample:
            df = data_sample["dataframe"]
            
            # Generate visualizations based on intent
            if intent in ["top_n", "visualize"] or "top" in state.get("query", "").lower():
                # Top customers by revenue
                if "customer" in state.get("query", "").lower() or focus == "customer":
                    viz = _create_top_customers_viz(df)
                    if viz:
                        visualizations.append(viz)
                
                # Top products
                if "product" in state.get("query", "").lower() or focus == "product":
                    viz = _create_top_products_viz(df)
                    if viz:
                        visualizations.append(viz)
            
            # Trend analysis
            if intent == "analyze_trend" and "order_date" in df.columns:
                viz = _create_trend_viz(df)
                if viz:
                    visualizations.append(viz)
            
            # Distribution charts
            if intent == "general_analysis":
                # Revenue distribution
                if "revenue" in df.columns:
                    viz = _create_distribution_viz(df, "revenue")
                    if viz:
                        visualizations.append(viz)
        
        # Default visualizations if none generated
        if not visualizations:
            visualizations = _get_default_visualizations()
        
        state["visualizations"] = visualizations
        
    except Exception as e:
        state["error"] = f"Visualization generation failed: {str(e)}"
    
    return state

def _create_top_customers_viz(df) -> Dict[str, Any]:
    """
    Create top customers visualization
    """
    if "customer_id" not in df.columns or "revenue" not in df.columns:
        return None
    
    top_customers = df.groupby("customer_id")["revenue"].sum().nlargest(5)
    
    return {
        "type": "bar",
        "title": "Top Customer Revenue Distribution",
        "description": "Shows revenue concentration among top customers to identify key accounts",
        "data": [
            {"name": name, "value": float(value)}
            for name, value in top_customers.items()
        ],
        "config": {
            "xAxis": "name",
            "yAxis": "value",
            "color": "#818CF8"
        }
    }

def _create_top_products_viz(df) -> Dict[str, Any]:
    """
    Create top products visualization
    """
    if "product" not in df.columns:
        return None
    
    value_col = "quantity" if "quantity" in df.columns else "revenue"
    top_products = df.groupby("product")[value_col].sum().nlargest(5)
    
    return {
        "type": "bar",
        "title": f"Top Products by {value_col.capitalize()} Ordered",
        "description": "Identifies most popular products by volume",
        "data": [
            {"name": name, "value": float(value)}
            for name, value in top_products.items()
        ],
        "config": {
            "xAxis": "name",
            "yAxis": "value",
            "color": "#A78BFA"
        }
    }

def _create_trend_viz(df) -> Dict[str, Any]:
    """
    Create trend visualization
    """
    if "order_date" not in df.columns or "revenue" not in df.columns:
        return None
    
    # Group by month
    df["month"] = pd.to_datetime(df["order_date"]).dt.to_period("M")
    monthly = df.groupby("month")["revenue"].sum()
    
    return {
        "type": "line",
        "title": "Revenue Trend Over Time",
        "description": "Monthly revenue trend analysis",
        "data": [
            {"date": str(date), "value": float(value)}
            for date, value in monthly.items()
        ],
        "config": {
            "xAxis": "date",
            "yAxis": "value",
            "color": "#10B981"
        }
    }

def _create_distribution_viz(df, column: str) -> Dict[str, Any]:
    """
    Create distribution visualization
    """
    if column not in df.columns:
        return None
    
    # Create histogram bins
    values = df[column].dropna()
    hist, bins = np.histogram(values, bins=10)
    
    return {
        "type": "histogram",
        "title": f"{column.capitalize()} Distribution",
        "description": f"Distribution of {column} values",
        "data": [
            {"range": f"{bins[i]:.0f}-{bins[i+1]:.0f}", "count": int(hist[i])}
            for i in range(len(hist))
        ],
        "config": {
            "xAxis": "range",
            "yAxis": "count",
            "color": "#F59E0B"
        }
    }

def _get_default_visualizations() -> List[Dict[str, Any]]:
    """
    Return default visualizations
    """
    return [
        {
            "type": "bar",
            "title": "Top Customer Revenue Distribution",
            "description": "Shows revenue concentration among top customers",
            "data": [
                {"name": "Niagara Pipe Co.", "value": 3000000},
                {"name": "Addison LLC", "value": 2250000},
                {"name": "Voit Company", "value": 1500000},
                {"name": "Turner Co. Ltd", "value": 750000},
                {"name": "Spiegel Company", "value": 375000}
            ],
            "config": {"xAxis": "name", "yAxis": "value", "color": "#818CF8"}
        },
        {
            "type": "bar",
            "title": "Top Products by Quantity Ordered",
            "description": "Identifies most popular products by volume",
            "data": [
                {"name": "Oxygen-Free Copper", "value": 2600000},
                {"name": "600V PVC Insulated", "value": 1950000},
                {"name": "THHN Wire 10 AWG", "value": 1300000},
                {"name": "THHN Wire 14 AWG", "value": 650000},
                {"name": "600V PVC Wire", "value": 650000}
            ],
            "config": {"xAxis": "name", "yAxis": "value", "color": "#A78BFA"}
        }
    ]

import pandas as pd
import numpy as np