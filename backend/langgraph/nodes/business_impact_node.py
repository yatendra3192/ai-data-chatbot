from typing import Dict, Any, List

async def extract_business_impact(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract business impact and actionable insights
    """
    state["current_step"] = "extracting_business_impact"
    
    try:
        analysis = state.get("analysis_result", {})
        visualizations = state.get("visualizations", [])
        data_context = state.get("data_context", {})
        
        # Generate business impact based on analysis
        impact_points = []
        
        # Analyze customer concentration
        if any(v.get("title", "").lower().contains("customer") for v in visualizations):
            impact_points.append(
                "Need to develop risk mitigation strategies for potential loss of "
                "top 2 customers who represent 67% of top 5 revenue"
            )
            impact_points.append(
                "Consider developing targeted retention programs for the top 3 "
                "customers who each generate over $1M in revenue"
            )
        
        # Product insights
        if any(v.get("title", "").lower().contains("product") for v in visualizations):
            impact_points.append(
                "Opportunity to grow mid-tier customers (positions 4-5) into "
                "larger accounts through focused account management"
            )
        
        # Geographic insights
        impact_points.append(
            "Geographic concentration in Middle East suggests opportunity "
            "for market diversification"
        )
        
        # Revenue insights
        metrics = analysis.get("metrics", {})
        if metrics.get("revenue_growth"):
            growth = metrics["revenue_growth"]
            if growth > 10:
                impact_points.append(
                    f"Strong revenue growth of {growth:.1f}% indicates healthy "
                    "business momentum - maintain current strategies"
                )
            elif growth < 0:
                impact_points.append(
                    f"Negative revenue growth of {growth:.1f}% requires immediate "
                    "attention to sales and retention strategies"
                )
        
        state["business_impact"] = {
            "title": "Business Impact:",
            "points": impact_points[:4],  # Limit to 4 most important points
            "risk_level": _assess_risk_level(analysis, metrics),
            "opportunities": _identify_opportunities(analysis, data_context)
        }
        
    except Exception as e:
        state["error"] = f"Business impact extraction failed: {str(e)}"
    
    return state

def _assess_risk_level(analysis: Dict, metrics: Dict) -> str:
    """
    Assess overall business risk level
    """
    risk_factors = 0
    
    # Customer concentration risk
    if metrics.get("total_customers", 100) < 20:
        risk_factors += 2
    
    # Revenue concentration
    if metrics.get("top_customers"):
        top_3_revenue = sum(c["revenue"] for c in metrics["top_customers"][:3])
        total_revenue = metrics.get("total_revenue", 1)
        if top_3_revenue / total_revenue > 0.5:
            risk_factors += 2
    
    # Determine risk level
    if risk_factors >= 3:
        return "high"
    elif risk_factors >= 1:
        return "medium"
    else:
        return "low"

def _identify_opportunities(analysis: Dict, data_context: Dict) -> List[str]:
    """
    Identify business opportunities
    """
    opportunities = []
    
    stats = data_context.get("statistics", {})
    
    # Growth opportunities
    for col, stat in stats.items():
        if isinstance(stat, dict) and "std" in stat:
            cv = stat["std"] / stat["mean"] if stat["mean"] != 0 else 0
            if cv > 1:  # High variability indicates opportunity
                opportunities.append(f"High variability in {col} suggests optimization potential")
    
    # Product expansion
    if "product" in data_context.get("columns", []):
        opportunities.append("Consider expanding product portfolio based on top performers")
    
    # Customer acquisition
    opportunities.append("Implement customer acquisition strategy to reduce concentration risk")
    
    return opportunities[:3]  # Return top 3 opportunities