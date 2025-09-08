from typing import Dict, Any, List
import pandas as pd
import numpy as np

def calculate_statistics(data: pd.DataFrame, columns: List[str] = None) -> Dict[str, Any]:
    """
    Calculate statistics for specified columns
    """
    if columns is None:
        columns = data.select_dtypes(include=[np.number]).columns.tolist()
    
    stats = {}
    for col in columns:
        if col in data.columns:
            stats[col] = {
                "mean": float(data[col].mean()),
                "median": float(data[col].median()),
                "std": float(data[col].std()),
                "min": float(data[col].min()),
                "max": float(data[col].max()),
                "quartiles": [
                    float(data[col].quantile(0.25)),
                    float(data[col].quantile(0.5)),
                    float(data[col].quantile(0.75))
                ]
            }
    return stats

def filter_data(data: pd.DataFrame, conditions: Dict[str, Any]) -> pd.DataFrame:
    """
    Filter data based on conditions
    """
    filtered = data.copy()
    
    for column, condition in conditions.items():
        if column not in filtered.columns:
            continue
            
        if isinstance(condition, dict):
            if "gt" in condition:
                filtered = filtered[filtered[column] > condition["gt"]]
            if "lt" in condition:
                filtered = filtered[filtered[column] < condition["lt"]]
            if "eq" in condition:
                filtered = filtered[filtered[column] == condition["eq"]]
            if "in" in condition:
                filtered = filtered[filtered[column].isin(condition["in"])]
        else:
            filtered = filtered[filtered[column] == condition]
    
    return filtered

def aggregate_data(data: pd.DataFrame, group_by: str, agg_func: str = "sum") -> pd.DataFrame:
    """
    Aggregate data by grouping column
    """
    numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
    if group_by in numeric_cols:
        numeric_cols.remove(group_by)
    
    agg_funcs = {col: agg_func for col in numeric_cols}
    
    return data.groupby(group_by).agg(agg_funcs).reset_index()

def detect_anomalies(data: pd.DataFrame, column: str, method: str = "iqr") -> List[int]:
    """
    Detect anomalies in data
    """
    if column not in data.columns:
        return []
    
    if method == "iqr":
        Q1 = data[column].quantile(0.25)
        Q3 = data[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        anomalies = data[(data[column] < lower_bound) | (data[column] > upper_bound)]
        return anomalies.index.tolist()
    
    elif method == "zscore":
        from scipy import stats
        z_scores = np.abs(stats.zscore(data[column].dropna()))
        threshold = 3
        anomalies = data.iloc[np.where(z_scores > threshold)[0]]
        return anomalies.index.tolist()
    
    return []

def generate_sql_query(natural_language: str, table_schema: Dict[str, str]) -> str:
    """
    Generate SQL query from natural language
    """
    # Simplified SQL generation - in production, use LLM
    query_lower = natural_language.lower()
    
    if "top" in query_lower and "customers" in query_lower:
        return "SELECT customer_id, SUM(revenue) as total_revenue FROM data GROUP BY customer_id ORDER BY total_revenue DESC LIMIT 5"
    elif "average" in query_lower:
        column = next((col for col in table_schema.keys() if col.lower() in query_lower), "revenue")
        return f"SELECT AVG({column}) as average FROM data"
    elif "count" in query_lower:
        return "SELECT COUNT(*) as total_count FROM data"
    else:
        return "SELECT * FROM data LIMIT 100"

def analyze_trends(data: pd.DataFrame, date_column: str, value_column: str) -> Dict[str, Any]:
    """
    Analyze trends in time series data
    """
    if date_column not in data.columns or value_column not in data.columns:
        return {"error": "Required columns not found"}
    
    # Convert to datetime if needed
    if not pd.api.types.is_datetime64_any_dtype(data[date_column]):
        data[date_column] = pd.to_datetime(data[date_column])
    
    # Sort by date
    data = data.sort_values(date_column)
    
    # Calculate trend metrics
    values = data[value_column].values
    dates = data[date_column].values
    
    # Simple linear regression for trend
    from scipy import stats
    x = np.arange(len(values))
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
    
    # Moving averages
    ma_7 = data[value_column].rolling(window=7).mean()
    ma_30 = data[value_column].rolling(window=30).mean()
    
    return {
        "trend_direction": "increasing" if slope > 0 else "decreasing",
        "trend_strength": abs(r_value),
        "slope": float(slope),
        "correlation": float(r_value),
        "p_value": float(p_value),
        "moving_avg_7": ma_7.tail(1).values[0] if len(ma_7) > 0 else None,
        "moving_avg_30": ma_30.tail(1).values[0] if len(ma_30) > 0 else None,
        "recent_change": float((values[-1] - values[-2]) / values[-2] * 100) if len(values) > 1 else 0
    }