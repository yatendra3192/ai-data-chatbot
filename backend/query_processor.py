import pandas as pd
import numpy as np
from typing import Dict, Any, List

def process_data_query(query: str, data: pd.DataFrame) -> Dict[str, Any]:
    """
    Process natural language queries and return actual data results
    """
    query_lower = query.lower()
    
    # Top/Bottom customers query
    if ("top" in query_lower or "bottom" in query_lower or "lowest" in query_lower or "highest" in query_lower) and "customer" in query_lower:
        # Extract number (default to 10)
        import re
        numbers = re.findall(r'\d+', query)
        n = int(numbers[0]) if numbers else 10
        
        # Determine if looking for top or bottom
        is_bottom = "bottom" in query_lower or "lowest" in query_lower
        
        # Get customers by revenue
        if 'customeridname' in data.columns and 'totalamount' in data.columns:
            customer_data = data[data['customeridname'].notna() & data['totalamount'].notna()]
            customer_revenue = customer_data.groupby('customeridname')['totalamount'].sum()
            
            if is_bottom:
                # Get bottom customers (excluding zero revenue)
                customer_revenue = customer_revenue[customer_revenue > 0]  # Exclude zero revenue
                selected_customers = customer_revenue.nsmallest(n)
                label = "bottom"
                title_label = "Bottom"
            else:
                # Get top customers
                selected_customers = customer_revenue.nlargest(n)
                label = "top"
                title_label = "Top"
            
            # Format response
            result_text = f"Here are the {label} {n} customers by revenue:\n\n"
            for i, (customer, revenue) in enumerate(selected_customers.items(), 1):
                result_text += f"{i}. {customer}: ${revenue:,.2f}\n"
            
            # Create visualization data
            viz_data = {
                "type": "bar",
                "title": f"{title_label} {n} Customers by Revenue",
                "data": [
                    {"name": str(customer)[:40], "value": float(revenue)}
                    for customer, revenue in selected_customers.items()
                ]
            }
            
            return {
                "answer": result_text,
                "visualization": viz_data,
                "metrics": {
                    "total_revenue": float(top_customers.sum()),
                    "average_revenue": float(top_customers.mean()),
                    "top_customer": str(top_customers.index[0]),
                    "top_customer_revenue": float(top_customers.iloc[0])
                }
            }
    
    # Revenue by status query
    elif "revenue" in query_lower and "status" in query_lower:
        if 'statuscode' in data.columns and 'totalamount' in data.columns:
            status_revenue = data.groupby('statuscode')['totalamount'].sum()
            status_map = {1: 'Active', 2: 'Submitted', 3: 'Canceled', 4: 'Fulfilled', 100: 'Invoiced'}
            
            result_text = "Revenue by Order Status:\n\n"
            for status, revenue in status_revenue.items():
                status_name = status_map.get(int(status), f"Status {status}")
                result_text += f"{status_name}: ${revenue:,.2f}\n"
            
            return {
                "answer": result_text,
                "visualization": {
                    "type": "bar",
                    "title": "Revenue by Order Status",
                    "data": [
                        {"name": status_map.get(int(status), f"Status {status}"), 
                         "value": float(revenue)}
                        for status, revenue in status_revenue.items()
                    ]
                }
            }
    
    # Monthly revenue trend
    elif "monthly" in query_lower or "trend" in query_lower:
        if 'modifiedon' in data.columns and 'totalamount' in data.columns:
            # Convert to datetime
            data['month'] = pd.to_datetime(data['modifiedon'], errors='coerce').dt.to_period('M')
            monthly_revenue = data.groupby('month')['totalamount'].sum()
            
            result_text = "Monthly Revenue Trend:\n\n"
            for month, revenue in monthly_revenue.tail(12).items():
                result_text += f"{month}: ${revenue:,.2f}\n"
            
            return {
                "answer": result_text,
                "visualization": {
                    "type": "line",
                    "title": "Monthly Revenue Trend",
                    "data": [
                        {"name": str(month), "value": float(revenue)}
                        for month, revenue in monthly_revenue.tail(12).items()
                    ]
                }
            }
    
    # Order statistics
    elif "order" in query_lower and ("count" in query_lower or "how many" in query_lower):
        total_orders = len(data)
        avg_order_value = data['totalamount'].mean() if 'totalamount' in data.columns else 0
        
        result_text = f"Order Statistics:\n\n"
        result_text += f"Total Orders: {total_orders:,}\n"
        result_text += f"Average Order Value: ${avg_order_value:,.2f}\n"
        
        if 'statuscode' in data.columns:
            status_counts = data['statuscode'].value_counts()
            result_text += "\nOrders by Status:\n"
            status_map = {1: 'Active', 2: 'Submitted', 3: 'Canceled', 4: 'Fulfilled', 100: 'Invoiced'}
            for status, count in status_counts.items():
                status_name = status_map.get(int(status), f"Status {status}")
                result_text += f"  {status_name}: {count:,}\n"
        
        return {"answer": result_text}
    
    # Default: return general statistics
    else:
        return {
            "answer": f"Dataset contains {len(data):,} sales orders with {len(data.columns)} columns. "
                     f"Ask specific questions like 'What are the top 10 customers?' or 'Show monthly revenue trend'."
        }