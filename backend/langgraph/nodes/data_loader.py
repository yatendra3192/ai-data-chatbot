from typing import Dict, Any
import pandas as pd
from pathlib import Path
from backend.data.csv_processor import CSVProcessor, DataCache

async def load_data(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load and prepare data for analysis
    """
    state["current_step"] = "loading_data"
    
    try:
        data_file = state.get("data_file")
        
        if not data_file:
            # Use sample data if no file provided
            state["data_sample"] = _get_sample_data()
        else:
            # Load actual CSV file
            processor = CSVProcessor()
            cache = DataCache()
            
            # Check cache first
            cache_key = Path(data_file).stem
            cached_data = cache.get(cache_key)
            
            if cached_data:
                state["data_sample"] = cached_data
            else:
                # Process CSV
                result = await processor.process_csv(data_file)
                state["data_sample"] = result
                
                # Cache the result
                cache.set(cache_key, result)
        
        # Extract key info for analysis
        if "data_sample" in state:
            sample = state["data_sample"]
            state["data_context"] = {
                "columns": sample.get("columns", []),
                "total_rows": sample.get("total_rows", 0),
                "statistics": sample.get("statistics", {}),
                "noun_mapping": sample.get("noun_mapping", {})
            }
    
    except Exception as e:
        state["error"] = f"Failed to load data: {str(e)}"
    
    return state

def _get_sample_data() -> Dict[str, Any]:
    """
    Generate sample B2B electrical supply data
    """
    import numpy as np
    
    # Create sample data
    customers = ["Niagara Pipe Co. Ltd", "Addison LLC", "Voit Company", 
                 "Turner Co. Ltd", "Spiegel Company", "Wagner Group",
                 "Mitchell Industries", "Cooper Electric", "Standard Cable",
                 "Phoenix Wire Co."]
    
    products = ["Oxygen-Free Copper Wire", "600 Volt PVC Insulated",
                "THHN Wire 10 AWG", "THHN Wire 14 AWG", "600 Volt PVC Insulated Wire",
                "Aluminum Building Wire", "XHHW-2 Wire", "MC Cable",
                "Flexible Metal Conduit", "Rigid Metal Conduit"]
    
    # Generate sample transactions
    n_rows = 1000
    data = []
    
    for i in range(n_rows):
        customer = np.random.choice(customers)
        product = np.random.choice(products)
        quantity = np.random.randint(10, 1000)
        unit_price = np.random.uniform(10, 500)
        revenue = quantity * unit_price
        
        # Weighted probability for top customers
        if customer in customers[:3]:
            quantity *= np.random.uniform(1.5, 3)
            revenue *= np.random.uniform(1.5, 3)
        
        data.append({
            "order_id": f"ORD{i+1000}",
            "customer_id": customer,
            "product": product,
            "quantity": int(quantity),
            "unit_price": round(unit_price, 2),
            "revenue": round(revenue, 2),
            "order_date": pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(0, 365)),
            "status": np.random.choice(["completed", "pending", "cancelled"], p=[0.7, 0.2, 0.1])
        })
    
    df = pd.DataFrame(data)
    
    # Calculate statistics
    processor = CSVProcessor()
    stats = processor._calculate_statistics(df)
    noun_mapping = processor._create_noun_mapping(df)
    
    return {
        "total_rows": len(df),
        "columns": df.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "sample": df.head(100).to_dict('records'),
        "statistics": stats,
        "dataframe": df,
        "noun_mapping": noun_mapping
    }