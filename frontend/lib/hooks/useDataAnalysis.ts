import { useState, useCallback, useEffect } from "react";
import { analyzeData } from "@/lib/api/dataAnalysis";

export function useDataAnalysis() {
  const [analysis, setAnalysis] = useState<any>(null);
  const [textSummary, setTextSummary] = useState<string>("");
  const [visualizations, setVisualizations] = useState<any[]>([]);
  const [businessImpact, setBusinessImpact] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<string[]>([]);
  const [sqlQuery, setSqlQuery] = useState<string>("");
  const [tableData, setTableData] = useState<any[]>([]);
  const [rowCount, setRowCount] = useState<number>(0);
  const [executionTime, setExecutionTime] = useState<number>(0);
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
                
                // Check for complete status - this contains all the data
                if (data.status === 'complete') {
                  console.log("[Stream] Complete response received");
                  
                  // Process all fields from the complete response
                  if (data.answer) {
                    console.log("[Stream] Answer received:", data.answer);
                    setAnalysis({ answer: data.answer, summary: data.answer });
                  }
                  if (data.text_summary) {
                    console.log("[Stream] Text summary received");
                    setTextSummary(data.text_summary);
                  }
                  if (data.visualizations) {
                    console.log("Received visualizations:", data.visualizations.length, "charts");
                    setVisualizations(data.visualizations);
                  }
                  if (data.sql_query) {
                    console.log("[Stream] SQL query received");
                    setSqlQuery(data.sql_query);
                  }
                  if (data.table_data) {
                    console.log("[Stream] Table data received:", data.table_data.length, "rows");
                    setTableData(data.table_data);
                  }
                  if (data.row_count !== undefined) {
                    console.log("[Stream] Row count:", data.row_count);
                    setRowCount(data.row_count);
                  }
                  if (data.execution_time !== undefined) {
                    console.log("[Stream] Execution time:", data.execution_time);
                    setExecutionTime(data.execution_time);
                  }
                  if (data.recommendations) {
                    setRecommendations(data.recommendations);
                  }
                  if (data.business_impact) {
                    setBusinessImpact(data.business_impact);
                  }
                }
                
                // Handle other status messages (processing, error)
                if (data.status === 'error') {
                  console.error("[Stream] Error:", data.error);
                  setError(data.error);
                }
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
    sqlQuery,
    tableData,
    rowCount,
    executionTime,
    isLoading,
    error,
    sendQuery
  };
}