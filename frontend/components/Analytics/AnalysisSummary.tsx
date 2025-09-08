import { Shield, TrendingUp, AlertCircle } from "lucide-react";

interface AnalysisSummaryProps {
  summary?: string;
  recommendations?: string[];
  isLoading?: boolean;
}

export function AnalysisSummary({ summary, recommendations = [], isLoading }: AnalysisSummaryProps) {
  const defaultSummary = "The data reveals a B2B electrical/cable supply business with significant revenue concentration among top customers. Product mix is dominated by industrial cables and wires, with high-voltage products being most popular. Order fulfillment shows consistent processing but notable cancellation rates.";
  
  const defaultRecommendations = [
    "Implement key account management program for top 5 customers who drive majority of revenue",
    "Investigate high order cancellation rate (24%) to identify and address root causes",
    "Consider inventory optimization for top 5 products by volume to ensure consistent availability",
    "Develop customer diversification strategy to reduce dependency on top accounts"
  ];

  const displaySummary = summary || defaultSummary;
  const displayRecommendations = recommendations.length > 0 ? recommendations : defaultRecommendations;

  return (
    <div className="bg-gradient-to-br from-indigo-600 to-purple-700 rounded-xl p-6 text-white shadow-lg">
      <div className="flex items-center gap-2 mb-4">
        <Shield className="w-6 h-6" />
        <h2 className="text-xl font-bold">AI Analysis Summary</h2>
      </div>
      
      {isLoading ? (
        <div className="animate-pulse">
          <div className="h-4 bg-white/20 rounded w-full mb-2"></div>
          <div className="h-4 bg-white/20 rounded w-3/4"></div>
        </div>
      ) : (
        <p className="text-white/90 mb-6 leading-relaxed">
          {displaySummary}
        </p>
      )}
      
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-5 h-5" />
          <h3 className="font-semibold">Recommendations:</h3>
        </div>
        
        {isLoading ? (
          <div className="animate-pulse space-y-2">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-3 bg-white/20 rounded w-full"></div>
            ))}
          </div>
        ) : (
          <ul className="space-y-2">
            {displayRecommendations.map((rec, index) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-white/60 mt-1">→</span>
                <span className="text-white/90 text-sm">{rec}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}