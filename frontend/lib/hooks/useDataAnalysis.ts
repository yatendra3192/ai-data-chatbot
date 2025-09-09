import { useState, useCallback, useEffect } from "react";
import { analyzeData } from "@/lib/api/dataAnalysis";

export function useDataAnalysis() {
  const [analysis, setAnalysis] = useState<any>(null);
  const [textSummary, setTextSummary] = useState<string>("");
  const [visualizations, setVisualizations] = useState<any[]>([]);
  const [businessImpact, setBusinessImpact] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load initial data on mount
  // useEffect(() => {
  //   sendQuery("Load initial dashboard data");
  // }, []);

  const sendQuery = useCallback(async (query: string, dataFile?: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await analyzeData(query, dataFile);
      
      // Handle streaming response
      if (response.stream) {
        const reader = response.stream.getReader();
        const decoder = new TextDecoder();
        
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          
          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                console.log("[Stream] Received data with keys:", Object.keys(data));
                
                // Check for analysis or answer field from backend
                if (data.analysis) {
                  console.log("[Stream] Analysis received:", data.analysis);
                  setAnalysis(data.analysis);
                } else if (data.answer) {
                  console.log("[Stream] Answer received:", data.answer);
                  setAnalysis({ answer: data.answer, summary: data.answer });
                }
                if (data.text_summary) {
                  console.log("[Stream] Text summary received:", data.text_summary);
                  setTextSummary(data.text_summary);
                }
                if (data.visualizations) {
                  console.log("Received visualizations:", data.visualizations.length, "charts");
                  console.log("First chart type:", data.visualizations[0]?.type);
                  console.log("All chart types:", data.visualizations.map((v: any) => v.type));
                  setVisualizations(data.visualizations);
                }
                if (data.business_impact) setBusinessImpact(data.business_impact);
                if (data.recommendations) setRecommendations(data.recommendations);
              } catch (e) {
                console.error("Failed to parse:", e);
              }
            }
          }
        }
      } else {
        // Handle regular response
        setAnalysis(response.analysis);
        setVisualizations(response.visualizations || []);
        setBusinessImpact(response.business_impact);
        setRecommendations(response.recommendations || []);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    analysis,
    textSummary,
    visualizations,
    businessImpact,
    recommendations,
    isLoading,
    error,
    sendQuery
  };
}