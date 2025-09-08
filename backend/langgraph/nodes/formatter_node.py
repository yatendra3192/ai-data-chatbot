from typing import Dict, Any

async def format_response(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the final response for the frontend
    """
    state["current_step"] = "formatting_response"
    
    try:
        # Extract all components
        analysis = state.get("analysis_result", {})
        visualizations = state.get("visualizations", [])
        business_impact = state.get("business_impact", {})
        recommendations = state.get("recommendations", [])
        
        # Format recommendations if they exist in analysis
        if not recommendations and analysis.get("insights"):
            recommendations = analysis["insights"]
        
        # Ensure we have default recommendations
        if not recommendations:
            recommendations = [
                "Implement key account management program for top 5 customers",
                "Investigate order patterns to optimize inventory",
                "Consider volume discounts for mid-tier customers",
                "Develop customer diversification strategy"
            ]
        
        # Format the complete response
        state["formatted_response"] = {
            "success": True,
            "analysis": {
                "summary": analysis.get("summary", "Analysis complete"),
                "metrics": analysis.get("metrics", {}),
                "patterns": analysis.get("patterns", [])
            },
            "visualizations": visualizations,
            "business_impact": business_impact,
            "recommendations": recommendations,
            "metadata": {
                "total_rows": state.get("data_context", {}).get("total_rows", 0),
                "columns": state.get("data_context", {}).get("columns", []),
                "processing_time": None  # Can add timing logic
            }
        }
        
    except Exception as e:
        state["error"] = f"Response formatting failed: {str(e)}"
        state["formatted_response"] = {
            "success": False,
            "error": str(e)
        }
    
    return state